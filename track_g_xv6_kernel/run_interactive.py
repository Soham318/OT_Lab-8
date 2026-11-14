#!/usr/bin/env python3
"""
Interactive QEMU driver for xv6-riscv.
Streams stdout, sends commands upon seeing the shell prompt ('$ '),
and captures all output until an exit condition or timeout.
"""

import sys
import os
import subprocess
import time

def run_commands(commands, timeout_sec=180, output_file=None, cwd=None):
    if cwd is None:
        if os.path.exists("xv6-riscv"):
            cwd = "xv6-riscv"
        elif os.path.exists("track_g_xv6_kernel/xv6-riscv"):
            cwd = "track_g_xv6_kernel/xv6-riscv"
        else:
            cwd = "."

    cmd = [
        "qemu-system-riscv64",
        "-machine", "virt",
        "-bios", "none",
        "-kernel", "kernel/kernel",
        "-m", "128M",
        "-smp", "3",
        "-nographic",
        "-global", "virtio-mmio.force-legacy=false",
        "-drive", "file=fs.img,if=none,format=raw,id=x0",
        "-device", "virtio-blk-device,drive=x0,bus=virtio-mmio-bus.0"
    ]

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    log_lines = []
    start_time = time.time()
    cmd_index = 0
    booted = False

    try:
        while time.time() - start_time < timeout_sec:
            # Non-blocking or line-based read
            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break
            if line:
                log_lines.append(line)
                sys.stdout.write(line)
                sys.stdout.flush()

                if "init: starting sh" in line or "$ " in line:
                    booted = True
                    if cmd_index < len(commands):
                        curr_cmd = commands[cmd_index]
                        cmd_index += 1
                        time.sleep(0.3)
                        proc.stdin.write(curr_cmd + "\n")
                        proc.stdin.flush()
                
                # Check if last command ran and produced prompt or finished
                if cmd_index >= len(commands) and ("ALL TESTS PASSED" in line or "FAILED" in line):
                    # Give a second for any trailing output
                    time.sleep(1)
                    break
    except Exception as e:
        log_lines.append(f"\nRunner Exception: {e}\n")
    finally:
        # Send Ctrl-A x to exit QEMU
        try:
            if proc.poll() is None:
                proc.stdin.write("\x01x")
                proc.stdin.flush()
                time.sleep(0.5)
        except Exception:
            pass

        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except Exception:
                proc.kill()

        # Read remaining
        rest, _ = proc.communicate()
        if rest:
            log_lines.append(rest)
            sys.stdout.write(rest)
            sys.stdout.flush()

    full_output = "".join(log_lines)
    if output_file:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_output)

    return full_output

if __name__ == "__main__":
    cmds = sys.argv[1:] if len(sys.argv) > 1 else ["echo 'Hello from xv6'", "ls"]
    run_commands(cmds, timeout_sec=120)

