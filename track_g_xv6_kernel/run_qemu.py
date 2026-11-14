#!/usr/bin/env python3
"""
Helper script to boot xv6-riscv in QEMU, run interactive commands,
capture console output, and cleanly terminate QEMU.
"""

import sys
import os
import subprocess
import time

def run_xv6(commands=None, timeout_sec=30, xv6_dir="xv6-riscv"):
    if not os.path.exists(xv6_dir):
        # Maybe we are inside track_g_xv6_kernel or root
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

    output = []
    start_time = time.time()
    commands_to_send = list(commands) if commands else []
    commands_sent = False

    try:
        # Give kernel 1.5s to boot
        time.sleep(1.5)
        if commands_to_send:
            for c in commands_to_send:
                proc.stdin.write(c + "\n")
                proc.stdin.flush()
                time.sleep(1.0)
            commands_sent = True
        
        # Let output accumulate or wait for timeout
        time_to_wait = max(2.0, min(timeout_sec, 60))
        # Wait up to timeout or until done
        deadline = time.time() + time_to_wait
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            time.sleep(0.5)

    except Exception as e:
        output.append(f"Exception during run: {e}\n")
    finally:
        # Send Ctrl-A x to cleanly terminate QEMU
        try:
            if proc.poll() is None:
                proc.stdin.write("\x01x")
                proc.stdin.flush()
                time.sleep(0.5)
        except Exception:
            pass

        # If still alive, terminate
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except Exception:
                proc.kill()

        stdout_data, _ = proc.communicate()
        if stdout_data:
            output.append(stdout_data)

    full_output = "".join(output)
    return full_output

if __name__ == "__main__":
    cmds = sys.argv[1:] if len(sys.argv) > 1 else ["echo 'xv6 boot successful'", "ls"]
    result = run_xv6(commands=cmds, timeout_sec=10)
    print("=== XV6 QEMU RUN OUTPUT ===")
    print(result)

