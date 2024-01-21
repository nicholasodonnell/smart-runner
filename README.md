<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./images/banner-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./images/banner-light.png">
  <img src="./images/banner-dark.png">
</picture>

[![Publish](https://github.com/nicholasodonnell/smart-runner/actions/workflows/publish.yml/badge.svg)](https://github.com/nicholasodonnell/smart-runner/actions/workflows/publish.yml)

## Description

S.M.A.R.T Runner is a Python script designed to automate the scheduling and execution of S.M.A.R.T (Self-Monitoring, Analysis, and Reporting Technology) tests on hard drives. It allows for regular short and long health checks on specified disks, helping in the early detection of potential disk failures.

## Features

- **Automated Scheduling:** Configure once and let the script handle regular short and long S.M.A.R.T tests.
- **Customizable Frequency:** Define how often each type of test should be performed on each disk.
- **Parallel Testing:** Specify how many disks to test simultaneously for both short and long tests.
- **Offset Timing:** Configure waiting periods between tests to avoid overloading the system or testing too frequently.
- **Logging:** Keep track of tests, results, and any errors in a specified log file.
- **Email Notifications:** Receive email alerts for test failures.
- **Configurable SMTP:** Set up custom SMTP server settings for sending out email notifications.
- **Easy Cron Integration:** Run the script as a daily cron job for hands-off operation.
- **Intelligent Disk Detection:** Automatically detect and handle disks based on mount points if specified.
- **Lock File:** Prevent multiple instances of the script from running simultaneously.

## Setup Requirements

Before using the S.M.A.R.T Runner, ensure the following requirements are met:

- **Python 3:** The script is written for Python 3. Ensure it is installed and properly configured on your system.
- **smartmontools:** This suite contains the `smartctl` utility, which is used to perform the S.M.A.R.T tests. It must be installed on your system.
    - Install it using your package manager, e.g., `sudo apt-get install smartmontools` on Debian/Ubuntu.
- **Root Access:** The script requires root permissions to access disk hardware for S.M.A.R.T tests.
- **Cron Job:** Schedule the script to run at least once per day using cron or another scheduler to automate the disk checks.

## Configuration

The script is configured via a `smart-runner.conf` file. Here's an explanation of each configuration option:

| Section    | Option           | Description                                                                                                                        |
| ---------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `disks`    | (list)           | List the devices or mounts to test. Devices are listed as `/dev/sdX`. If a mount is given the disk will automatically be resolved. |
| `database` | `file`           | Path to the file where test dates are stored.                                                                                      |
| `short`    | `enabled`        | Set to `true` to enable short SMART tests.                                                                                         |
|            | `frequency_days` | How often (in days) to run a short test on each disk.                                                                              |
|            | `disks_per_run`  | Number of disks to test in parallel for short tests. Set to 0 for all.                                                             |
|            | `offset_days`    | Time to wait (in days) before running a short test on a different disk.                                                            |
| `long`     | `enabled`        | Set to `true` to enable long SMART tests.                                                                                          |
|            | `frequency_days` | How often (in days) to run a long test on each disk.                                                                               |
|            | `disks_per_run`  | Number of disks to test in parallel for long tests. Set to 0 for all.                                                              |
|            | `offset_days`    | Time to wait (in days) before running a long test on a different disk.                                                             |
| `log`      | `file`           | Path to the log file where execution details are recorded.                                                                         |
|            | `level`          | Log level. Set to `debug` for more detailed logs.                                                                                  |
| `email`    | `enabled`        | Set to `true` to enable email notifications for test failures.                                                                     |
|            | `from_email`     | Sender email address for notifications.                                                                                            |
|            | `to_email`       | Recipient email address for notifications.                                                                                         |
| `smtp`     | `host`           | SMTP server for sending email notifications.                                                                                       |
|            | `port`           | SMTP server port. Leave empty for default port.                                                                                    |
|            | `ssl`            | Set to `true` to enable SSL for the SMTP connection.                                                                               |
|            | `tls`            | Set to `true` to enable TLS for the SMTP connection.                                                                               |
|            | `user`           | SMTP server username for authentication.                                                                                           |
|            | `password`       | SMTP server password for authentication.                                                                                           |

## Usage

1. Clone this repository:
   ```console
   git clone https://github.com/nicholasodonnell/smart-runner.git
   ```
2. Create a `smart-runner.conf` configuration file according to your needs using [`smart-runner.conf.example`](./smart-runner.conf.example) as a reference:
   ```console
   cp smart-runner.conf.example smart-runner.conf
   ```
3. Schedule the script to run via a cron job (edit using `crontab -e`):
   ```console
   0 3 * * * /path/to/smart-runner.py --conf=/path/to/smart-runner.conf
   ```
4. Monitor the specified log file or your email for notifications about disk health.
