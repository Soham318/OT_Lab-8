#!/usr/bin/env python3
"""
Robust non-blocking runner for xv6-riscv workloads.
Launches QEMU, waits for shell prompt, sends command, monitors for completion,
sends Ctrl-A x cleanly, and saves raw output to results/.
"""

import sys
import os
import subprocess
import threading
import time

def run_single_workload(command, timeout_sec=45, output_file=None, xv6_dir="xv6-riscv"):
    if not os.path.exists(xv6_dir):
        if os.path.exists(os.path.join("track_g_xv6_kernel", "xv6-riscv")):
            xv6_dir = os.path.join("track_g_xv6_kernel", "xv6-riscv")
        elif os.path.exists("../xv6-riscv"):
            xv6_dir = "../xv6-riscv"

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
        cwd=xv6_dir,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    output_lines = []
    done_event = threading.Event()
    command_sent_event = threading.Event()

    def reader():
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            output_lines.append(line)
            sys.stdout.write(line)
            sys.stdout.flush()

            # Detect initial shell prompt
            if ("init: starting sh" in line or "$ " in line) and not command_sent_event.is_set():
                command_sent_event.set()

            # If command was already sent, check for completion
            stripped = line.strip()
            if command_sent_event.is_set():
                if any(term in line for term in ["Completed Successfully", "ALL TESTS PASSED", "Granularity Findings", "VALIDATION CHECKS PASSED"]):
                    time.sleep(1.0)
                    done_event.set()
                elif stripped == "$" and len(output_lines) > 8:
                    # Shell prompt returned strictly after command execution
                    time.sleep(0.5)
                    done_event.set()

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    # Wait for prompt to send command
    prompt_seen = command_sent_event.wait(timeout=10)
    if prompt_seen:
        time.sleep(0.5)
        proc.stdin.write(command + "\n")
        proc.stdin.flush()
    else:
        output_lines.append(f"\n[ERROR] Shell prompt not seen within 10s.\n")
        done_event.set()

    # Wait for workload completion or timeout
    finished = done_event.wait(timeout=timeout_sec)
    if not finished:
        output_lines.append(f"\n[WARNING] Workload timed out after {timeout_sec}s.\n")

    # Cleanly terminate QEMU with Ctrl-a x
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

    t.join(timeout=2)
    full_text = "".join(output_lines)

    if output_file:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"\n[INFO] Output saved to: {output_file}")

    return full_text

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cpu_workload"
    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    run_single_workload(cmd, timeout_sec=40, output_file=out_file)
