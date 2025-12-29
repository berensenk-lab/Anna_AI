# Filename: BASE/core/cognitive_loop_manager.py
"""
Cognitive Loop Manager - WITH CRASH RECOVERY
=============================================
Agent decides with <speak>YES/NO</speak> - that's it
FIXED: Autonomous responses now properly saved to memory
NEW: Crash recovery with configurable auto-restart (AUTO_RESTART control)

Crash Recovery Behavior:
- When AUTO_RESTART=True: Auto-restarts up to 3 times with exponential backoff
- When AUTO_RESTART=False: Stops completely on first error, requires manual restart
- Manual restart always available via restart_cognition()
"""

import asyncio
import time
import traceback
from typing import Optional
from BASE.core.logger import Logger
from BASE.core.cognitive_loop_recovery import CognitiveLoopRecovery


class CognitiveLoopManager:
    """Manages continuous autonomous thinking loop with crash recovery"""
    
    __slots__ = (
        'thought_processor', 'controls', 'logger', 'is_running', 'loop_task',
        'total_cycles', 'reactive_cycles', 'proactive_cycles', 'idle_cycles',
        'last_stats_log', 'last_response_time', 'min_response_interval',
        'autonomous_response_callback', 'recovery', 'ai_core_ref'
    )
    
    def __init__(self, thought_processor, controls, logger: Logger):
        self.thought_processor = thought_processor
        self.controls = controls
        self.logger = logger
        
        self.is_running = False
        self.loop_task = None
        
        # Statistics
        self.total_cycles = 0
        self.reactive_cycles = 0
        self.proactive_cycles = 0
        self.idle_cycles = 0
        self.last_stats_log = time.time()
        
        # Response rate limiting
        self.last_response_time = 0.0
        self.min_response_interval = 30.0
        
        # Callback for autonomous responses
        self.autonomous_response_callback = None
        
        # AI Core reference
        self.ai_core_ref = None
        
        # NEW: Crash recovery manager
        self.recovery = CognitiveLoopRecovery(
            controls=controls,
            logger=logger,
            max_auto_restarts=3,
            initial_cooldown=5.0,
            success_threshold=300.0,  # 5 minutes of success resets counter
            max_backoff=30.0
        )
        
        self.logger.system("[Cognitive Loop] Recovery system initialized")
    
    async def start_continuous_loop(self):
        """Start the continuous cognitive loop"""
        if self.is_running:
            self.logger.warning("[Cognitive Loop] Already running")
            return
        
        self.is_running = True
        self.logger.system("[Cognitive Loop] Starting - Agent decides with <speak>YES/NO</speak>")
        
        # Update response interval
        SLOW_MODE = getattr(self.controls, 'SLOW_MODE', False)
        if SLOW_MODE:
            delay = getattr(self.controls, 'DELAY_TIMER', 30)
            self.min_response_interval = delay
            self.logger.system(f"[Cognitive Loop] Response rate limiting: 1 per {delay}s")
        else:
            self.min_response_interval = 30.0
            self.logger.system("[Cognitive Loop] No response rate limiting")
        
        # Record loop start for recovery tracking
        self.recovery.on_loop_start()
        
        self.loop_task = asyncio.create_task(self._cognitive_loop())
    
    async def stop_continuous_loop(self):
        """Stop the cognitive loop gracefully"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.system("[Cognitive Loop] Stopping...")
        
        if self.loop_task:
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                pass
        
        self.logger.system("[Cognitive Loop] Stopped")
    
    async def restart_cognition(self):
        """
        Manually restart the cognitive loop
        This resets the crash counter and allows restart regardless of crash count
        """
        self.logger.system("[Cognitive Loop] Manual restart requested")
        
        # Request manual restart (resets crash counter)
        self.recovery.request_manual_restart()
        
        # Stop current loop if running
        if self.is_running:
            await self.stop_continuous_loop()
            await asyncio.sleep(1.0)  # Brief pause
        
        # Start fresh loop
        await self.start_continuous_loop()
        
        self.logger.system("[SUCCESS] [Cognitive Loop] Manual restart complete")
    
    async def _cognitive_loop(self):
        """
        Main cognitive loop with crash recovery
        """
        self.logger.system("[Cognitive Loop] Agent-driven response mode")
        
        while self.is_running:
            try:
                # Kill command check
                if self.thought_processor.thought_buffer.is_shutdown_requested():
                    self.logger.system("[Cognitive Loop] Kill command - STOPPING")
                    self.is_running = False
                    break
                
                if hasattr(self, 'ai_core_ref') and self.ai_core_ref:
                    if self.ai_core_ref.shutdown_flag.is_set():
                        self.logger.system("[Cognitive Loop] AI Core shutdown - STOPPING")
                        self.is_running = False
                        break
                
                self.total_cycles += 1
                
                # ============================================================
                # PROCESS THOUGHTS (reactive or proactive)
                # Agent outputs <speak>YES/NO</speak> during this
                # ============================================================
                context_parts = await self.thought_processor.thinking_modes.build_thought_context()
                processing_occurred = await self.thought_processor.process_thoughts(
                    context_parts=context_parts
                )
                
                if processing_occurred:
                    # Track cycle type
                    if self.thought_processor.thought_buffer.get_unprocessed_events():
                        self.reactive_cycles += 1
                        cycle_type = "reactive"
                    else:
                        self.proactive_cycles += 1
                        cycle_type = "proactive"
                    
                    stats = self.thought_processor.thought_buffer.get_thinking_stats()
                    time_since_user = self.thought_processor.thought_buffer.get_time_since_last_user_input()
                    
                    self.logger.thinking(
                        f"[Loop] Cycle {self.total_cycles} ({cycle_type}) | "
                        f"Stream: {stats['consecutive_proactive']} | "
                        f"Momentum: {stats['momentum']:.2f} | "
                        f"Last input: {time_since_user:.0f}s ago"
                    )
                else:
                    self.idle_cycles += 1
                    self.thought_processor.thought_buffer.decay_momentum()
                
                # ============================================================
                # CHECK IF AGENT SAID <speak>YES</speak>
                # SIMPLIFIED: Just a boolean check, no reason
                # ============================================================
                should_speak = self.thought_processor.thought_buffer.should_speak()
                
                if should_speak:
                #     self.logger.system("[Agent Decision] <speak>YES</speak>")
                    
                    # Generate response (will clear flag after checking it)
                    await self._generate_response()
                
                # ============================================================
                # ADAPTIVE PACING
                # ============================================================
                time_since_user = self.thought_processor.thought_buffer.get_time_since_last_user_input()
                
                if time_since_user < 600:  # < 10 minutes
                    if processing_occurred:
                        await asyncio.sleep(0.05)  # 50ms
                    else:
                        await asyncio.sleep(0.2)  # 200ms
                else:  # 10+ minutes idle
                    if processing_occurred:
                        await asyncio.sleep(0.5)  # 500ms
                    else:
                        await asyncio.sleep(2.0)  # 2s
                
                # Periodic stats
                if time.time() - self.last_stats_log > 120.0:
                    self._log_statistics()
                    self.last_stats_log = time.time()
            
            except asyncio.CancelledError:
                self.logger.system("[Cognitive Loop] Cancelled")
                break
                
            except Exception as e:
                # ============================================================
                # CRASH RECOVERY LOGIC
                # ============================================================
                self.logger.error(f"[Cognitive Loop] CRASH: {type(e).__name__}: {e}")
                
                # Get full traceback
                tb_str = traceback.format_exc()
                self.logger.error(f"[Cognitive Loop] Traceback:\n{tb_str}")
                
                # Report crash to recovery manager
                should_auto_restart = self.recovery.on_crash(
                    error=e,
                    traceback_str=tb_str,
                    cycle_count=self.total_cycles
                )
                
                if should_auto_restart:
                    # Auto-restart approved
                    cooldown = self.recovery.get_current_cooldown()
                    self.logger.warning(
                        f"[Recovery] AUTO-RESTART in {cooldown:.1f}s "
                        f"(Crash {self.recovery.crash_count}/{self.recovery.max_auto_restarts})"
                    )
                    
                    # Wait for cooldown
                    await asyncio.sleep(cooldown)
                    
                    # Check if we should still restart (user might have stopped it)
                    if not self.is_running:
                        self.logger.system("[Recovery] Restart cancelled (loop stopped)")
                        break
                    
                    self.logger.system("[Recovery] Auto-restarting cognitive loop...")
                    
                    # Reset loop task and continue
                    self.recovery.successful_restarts += 1
                    self.recovery.on_loop_start()  # Record restart time
                    
                    continue  # Loop continues
                    
                else:
                    # Auto-restart not allowed
                    self.is_running = False
                    
                    auto_restart_enabled = getattr(self.controls, 'AUTO_RESTART', True)
                    
                    if not auto_restart_enabled:
                        self.logger.error(
                            "[Recovery] STOPPED - AUTO_RESTART is disabled\n"
                            "[Recovery] Loop will not restart automatically\n"
                            "[Recovery] Use restart_cognition() or GUI button to restart"
                        )
                    else:
                        self.logger.error(
                            f"[Recovery] STOPPED - Maximum auto-restarts exceeded ({self.recovery.max_auto_restarts})\n"
                            "[Recovery] Manual restart required\n"
                            "[Recovery] Use restart_cognition() or GUI button to restart"
                        )
                    
                    break  # Exit loop
        
        self.logger.system("[Cognitive Loop] STOPPED")

    async def _generate_response(self):
        """
        Generate autonomous spoken response
        FIXED: Add response echo to thoughts and clear trigger only after success
        """
        # Rate limiting check
        time_since_last_response = time.time() - self.last_response_time
        SLOW_MODE = getattr(self.controls, 'SLOW_MODE', False)
        
        if SLOW_MODE and time_since_last_response < self.min_response_interval:
            remaining = self.min_response_interval - time_since_last_response
            # self.logger.system(f"[Autonomous] Rate limited - {remaining:.0f}s remaining")
            self.thought_processor.thought_buffer.response_trigger.clear()
            return
        
        # Check AI core
        if not hasattr(self, 'ai_core_ref') or not self.ai_core_ref:
            self.logger.warning("[Autonomous] No AI core - cannot generate")
            self.thought_processor.thought_buffer.response_trigger.clear()
            return
        
        try:
            # self.logger.system("[Autonomous] Generating spoken response...")
            
            # Use processing_delegator to generate response
            if hasattr(self.ai_core_ref, 'processing_delegator'):
                delegator = self.ai_core_ref.processing_delegator
                
                # Generate autonomous response
                response = await delegator._generate_responsive_response(
                    user_text="",  # Empty = autonomous
                    context_parts=[],
                    chat_context=None,
                    is_chat_engagement=False
                )
                
                if response:
                    # self.logger.system(f"[Autonomous] Generated: {response[:60]}...")
                    
                    # CRITICAL FIX 1: Add response echo to thought buffer FIRST
                    thought_buffer = self.thought_processor.thought_buffer
                    thought_buffer.add_response_echo(
                        response_text=response,
                        timestamp=time.time()
                    )
                    # self.logger.system("[Autonomous] Response echo added to thoughts")
                    
                    # Save to memory (autonomous responses need explicit save)
                    if hasattr(self.ai_core_ref, 'memory_manager'):
                        memory_mgr = self.ai_core_ref.memory_manager
                        if self.controls.SAVE_MEMORY:
                            saved_entry = memory_mgr.save_bot_response(response)
                            
                            if saved_entry:
                                self.logger.memory(
                                    f"[Autonomous] Saved (Short: {len(memory_mgr.short_memory)})"
                                )
                        else:
                            self.logger.warning("[Autonomous] Memory save disabled")
                    
                    # CRITICAL FIX 2: Call the callback to queue for GUI
                    if self.autonomous_response_callback:
                        try:
                            self.logger.system("[Autonomous] Calling GUI callback...")
                            self.autonomous_response_callback(response)
                            self.logger.system("[Autonomous] [SUCCESS] Response queued for GUI")
                            
                            # CRITICAL FIX 3: Clear trigger ONLY after successful callback
                            thought_buffer.response_trigger.clear()
                            # self.logger.system("[Autonomous] Response trigger cleared")
                            
                        except Exception as e:
                            self.logger.error(f"[Autonomous] Callback error: {e}")
                            traceback.print_exc()
                            # Don't clear trigger on callback failure - allow retry
                            return
                    else:
                        self.logger.error("[Autonomous] [FAILED] No callback registered!")
                        # Don't clear trigger if no callback - system issue
                        return
                    
                    # Update timestamp (only after successful callback)
                    self.last_response_time = time.time()
                else:
                    self.logger.warning("[Autonomous] Empty response")
                    # Clear trigger on empty response
                    self.thought_processor.thought_buffer.response_trigger.clear()
            else:
                self.logger.error("[Autonomous] No processing_delegator")
                self.thought_processor.thought_buffer.response_trigger.clear()
            
        except Exception as e:
            self.logger.error(f"[Autonomous] Error: {e}")
            traceback.print_exc()
            # Clear trigger on exception to prevent infinite retry
            self.thought_processor.thought_buffer.response_trigger.clear()

    def set_ai_core(self, ai_core):
        """Inject AI core reference"""
        self.ai_core_ref = ai_core
        # No nested cognitive_loop - this IS the cognitive loop manager
        # The ai_core reference is now set and will be used during loop execution
        
    def _log_statistics(self):
        """Log statistics"""
        total = self.total_cycles
        if total == 0:
            return
        
        reactive = self.reactive_cycles
        proactive = self.proactive_cycles
        idle = self.idle_cycles
        
        reactive_pct = (reactive / total * 100)
        proactive_pct = (proactive / total * 100)
        idle_pct = (idle / total * 100)
        
        self.logger.system(
            f"[Loop Stats] Total: {total} | "
            f"Reactive: {reactive} ({reactive_pct:.1f}%) | "
            f"Proactive: {proactive} ({proactive_pct:.1f}%) | "
            f"Idle: {idle} ({idle_pct:.1f}%)"
        )
    
    def get_statistics(self) -> dict:
        """Get comprehensive statistics including recovery stats"""
        base_stats = {
            'total_cycles': self.total_cycles,
            'reactive_cycles': self.reactive_cycles,
            'proactive_cycles': self.proactive_cycles,
            'idle_cycles': self.idle_cycles,
            'is_running': self.is_running,
            'last_response_time': self.last_response_time,
            'min_response_interval': self.min_response_interval
        }
        
        # Add recovery statistics
        recovery_stats = self.recovery.get_statistics()
        base_stats['recovery'] = recovery_stats
        
        return base_stats
    
    def get_recovery_status(self) -> str:
        """Get formatted recovery status string"""
        return self.recovery.format_crash_summary()