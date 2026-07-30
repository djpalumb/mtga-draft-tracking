import time
import shutil

def simulate_running_log(
    input_path,
    output_path,
    interval_ms=100,
    start_line=0,
    initial_wait_s=3,
):
    """
    Copy a logfile up to start_line immediately, then append the rest
    gradually to simulate a running logfile.

    Args:
        input_path: Existing logfile to replay.
        output_path: Synthetic logfile to write.
        interval_ms: Delay between appended lines.
        start_line: Number of lines to write immediately before starting.
                    (0-indexed: start_line=100 writes lines 0-100 immediately)
        initial_wait_s: Seconds to wait after initial write before replaying.
    """

    # Read entire source log
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if start_line >= len(lines):
        raise ValueError(
            f"start_line {start_line} exceeds logfile length {len(lines)}"
        )

    # Write initial state
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines[:start_line])

    print(f"Wrote initial {start_line} lines")
    print(f"Waiting {initial_wait_s}s before replay...")

    time.sleep(initial_wait_s)

    # Append remaining lines slowly
    delay = interval_ms / 1000.0

    with open(output_path, "a", encoding="utf-8") as f:
        for i, line in enumerate(lines[start_line:], start=start_line):
            f.write(line)
            f.flush()  # Important: make listener see the update

            print(f"Appended line {i}")

            time.sleep(delay)

    print("Replay complete")



if __name__ == '__main__':
    import os
    LOGFILE_IN = os.path.join('test_files', 'sample_draft_logs_full.log')
    LOGFILE_OUT = os.path.join('test_files', 'sample_draft_logs.log')

    simulate_running_log(
        input_path=LOGFILE_IN,
        output_path=LOGFILE_OUT,
        interval_ms=1000,
        start_line=20,
        initial_wait_s=5
    )