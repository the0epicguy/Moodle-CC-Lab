# Practical: Configure Auto Scaling Groups in AWS

## 1. Aim

To configure an Auto Scaling Group (ASG) in Amazon Web Services (AWS) and observe automatic provisioning and removal of EC2 instances under changing workloads.

## 2. Objectives

- Create an EC2 launch template.
- Configure an Auto Scaling Group with minimum, desired, and maximum capacity.
- Attach a target tracking scaling policy based on average CPU utilization.
- Generate CPU load on an EC2 instance.
- Observe automatic scale-out when CPU utilization increases.
- Stop the workload and observe automatic scale-in when CPU utilization decreases.

## 3. Services and tools used

| Service / tool | Purpose |
|---|---|
| Amazon EC2 | Provides the virtual machines used by the Auto Scaling Group. |
| EC2 Launch Template | Stores the configuration used when the ASG launches new instances. |
| EC2 Auto Scaling | Maintains the required number of instances and changes capacity in response to demand. |
| Amazon CloudWatch | Collects CPU metrics and evaluates scaling alarms. |
| AWS Systems Manager Session Manager | Provides browser-based access to the EC2 instance without requiring an inbound SSH connection. |
| `stress-ng` | Generates CPU load to test the scaling policy. |

## 4. Configuration used

The practical was performed in the **US East (N. Virginia) region (`us-east-1`)**.

| Setting | Value |
|---|---|
| Auto Scaling Group | `CC-Lab-ASG` |
| Launch Template | `CC-Lab-Template` |
| Instance type | `t3.micro` |
| Operating system | Amazon Linux 2023 |
| Minimum capacity | 1 instance |
| Desired capacity | 1 instance |
| Maximum capacity | 3 instances |
| Scaling policy | Target tracking |
| Scaling metric | Average CPU utilization |
| CPU utilization target | 30% |
| Instance warmup | 120 seconds |
| Scale-in | Enabled |

The security group used an inbound HTTP rule on TCP port 80 from `0.0.0.0/0`. It also had an SSH rule on TCP port 22 restricted to the configured client IP. Session Manager was used for command-line access, so SSH was not required for the workload test.

> **Note:** AWS console labels and layouts can change. The values above describe the configuration used in this practical.

## 5. Procedure

### Step 1: Open the AWS Management Console

1. Open the AWS Management Console.
2. Sign in to the AWS account.
3. Select the **US East (N. Virginia)** region (`us-east-1`) from the region selector.
4. Open the **EC2** service.

### Step 2: Create the launch template

A launch template defines the configuration AWS uses when creating EC2 instances for the Auto Scaling Group.

1. In the EC2 console, open **Launch Templates** under **Instances**.
2. Select **Create launch template**.
3. Enter the launch template name: `CC-Lab-Template`.
4. Add a description if required.
5. Select an Amazon Linux 2023 AMI.
6. Select the instance type `t3.micro`.
7. Select or create the security group used for the practical.
8. Configure the required storage and key-pair options if prompted. A key pair was not needed for the Session Manager access method.
9. Review the configuration and create the launch template.

### Step 3: Configure the security group

The security group controls network traffic to and from the EC2 instances.

The security group used for the practical had these rules:

| Direction | Type | Protocol / port | Source / destination |
|---|---|---|---|
| Inbound | HTTP | TCP 80 | `0.0.0.0/0` |
| Inbound | SSH | TCP 22 | The configured client IP address, restricted to `/32` |
| Outbound | All traffic | All | `0.0.0.0/0` |

The HTTP rule allows web traffic to reach the instance. The SSH rule was restricted to a single client IP rather than being open to everyone. Session Manager access uses the instance's outbound connection to AWS Systems Manager and does not require an inbound SSH rule.

### Step 4: Create the Auto Scaling Group

1. In the EC2 console, open **Auto Scaling Groups** under **Auto Scaling**.
2. Select **Create Auto Scaling group**.
3. Enter the name `CC-Lab-ASG`.
4. Select the launch template `CC-Lab-Template`.
5. Continue to the network settings.
6. Select the VPC and subnets for the practical. The instance used the default VPC and a subnet in Availability Zone `us-east-1a`.
7. Continue through the optional load balancing and health-check settings. A load balancer was not required for this CPU-based scaling demonstration.
8. Set the group capacity:
   - Desired capacity: `1`
   - Minimum capacity: `1`
   - Maximum capacity: `3`
9. Review the settings and create the Auto Scaling Group.

The minimum capacity ensures that the group keeps at least one instance running. The maximum capacity limits the group to three instances. The desired capacity is the number of instances the group initially attempts to maintain.

### Step 5: Verify the initial instance

1. Open the newly created Auto Scaling Group.
2. Check the **Instance management** or **Instances** section.
3. Wait for the first EC2 instance to launch.
4. Confirm that its lifecycle state is **InService** and its health status is **Healthy**.
5. Open the EC2 Instances page and verify that the instance is running.

At this stage, the group should have one running instance.

### Step 6: Configure access through Systems Manager Session Manager

Session Manager was used to access the instance through the AWS Console. This avoided relying on an SSH connection.

1. Open **IAM** in the AWS Console.
2. Create an IAM role for an EC2 service.
3. Attach the AWS-managed policy `AmazonSSMManagedInstanceCore`.
4. Name the role `CC-Lab-SSM-Role` and create it.
5. Open the EC2 instance details.
6. Choose **Actions → Security → Modify IAM role**.
7. Attach `CC-Lab-SSM-Role` to the instance.
8. Allow time for the instance to obtain the role credentials. In this practical, the instance was rebooted and then given time to register successfully.
9. Open **Connect** on the EC2 instance and choose **Session Manager**.
10. Select **Connect**. Once the session opens, a browser-based terminal is available.

If Session Manager initially reports that it cannot obtain credentials or that an instance management role is not configured, verify that the role is attached to the instance, that `AmazonSSMManagedInstanceCore` is attached to the role, and that the instance has outbound network connectivity. Allow time for the change to take effect and retry.

### Step 7: Install `stress-ng`

`stress-ng` is a Linux utility that can generate controlled CPU load.

In the Session Manager terminal, run:

```bash
sudo dnf update -y
sudo dnf install stress-ng -y
```

Verify that it is installed:

```bash
stress-ng --version
```

The practical used `stress-ng` version `0.15.05`.

### Step 8: Create the target tracking scaling policy

1. Open **EC2 → Auto Scaling Groups**.
2. Select `CC-Lab-ASG`.
3. Open the **Automatic scaling** tab.
4. Choose to create a dynamic scaling policy.
5. Select **Target tracking scaling policy**.
6. Set the policy name to `CPU-Target-Tracking`.
7. Select **Average CPU utilization** as the metric.
8. Set the target value to `30`.
9. Set instance warmup to `120` seconds.
10. Ensure that scale-in is enabled.
11. Create the policy.

The target tracking policy uses CloudWatch metrics and alarms to adjust the number of instances. When the group's average CPU utilization remains above the target, the policy can add capacity. When utilization falls, it can remove excess capacity, subject to the group's minimum capacity and AWS scaling safeguards.

### Step 9: Generate high CPU utilization

1. Connect to the original EC2 instance using Session Manager.
2. Run the following command:

```bash
sudo stress-ng --cpu 2 --cpu-load 100 --timeout 600s
```

What the command means:

- `sudo`: runs the command with elevated privileges.
- `stress-ng`: starts the workload generator.
- `--cpu 2`: creates two CPU workers.
- `--cpu-load 100`: asks each worker to generate 100% CPU load.
- `--timeout 600s`: stops the workload after 600 seconds, or 10 minutes.

Keep the Session Manager session open if you want to inspect the process. The workload is intended to raise CPU utilization so that the target tracking policy can respond.

### Step 10: Observe scale-out

1. Open the `CC-Lab-ASG` page.
2. Watch the **Instance management** section.
3. Check the **Activity** or **Activity history** tab for scaling events.
4. Wait for CloudWatch to collect and evaluate the CPU metrics.
5. Observe the ASG launch additional EC2 instances as CPU demand increases.
6. Confirm that the newly launched instances become **InService** and **Healthy**.

During the test, the group scaled out from its initial capacity and launched additional instances, up to the configured maximum of three.

Scaling is not necessarily immediate. Metric collection, alarm evaluation, instance launch time, and warmup can all introduce delays.

### Step 11: Stop the workload and observe scale-in

The stress test was configured to stop automatically after 10 minutes. After it stopped:

1. Allow CPU utilization to fall.
2. Check the instance CPU metrics and the group's average CPU utilization.
3. Return to the Auto Scaling Group's **Instance management** and **Activity history** sections.
4. Wait for CloudWatch and the target tracking policy to evaluate the lower utilization.
5. Observe AWS terminate excess instances automatically.
6. Confirm that the group returns to one healthy instance, matching its minimum and desired capacity.

The group successfully scaled in after CPU utilization dropped. It retained one instance because the minimum capacity was set to 1.

Scale-in can take several minutes. Target tracking is deliberately conservative when removing capacity, and AWS may wait for metric evaluation, instance warmup, and stabilization before terminating instances. Do not manually terminate instances during the demonstration because the objective is to observe automatic scale-in.

## 6. Commands used

### Update package information and install the workload tool

```bash
sudo dnf update -y
sudo dnf install stress-ng -y
```

### Check the installed version

```bash
stress-ng --version
```

### Generate CPU load for 10 minutes

```bash
sudo stress-ng --cpu 2 --cpu-load 100 --timeout 600s
```

### Check whether a stress-ng process is still running

```bash
pgrep -af stress-ng
```

If the stress test has completed, this command should not show an active stress-ng workload.

## 7. How Auto Scaling worked

The practical used a target tracking policy with a target average CPU utilization of 30%.

**Scale-out sequence:**

1. The `stress-ng` command increased CPU usage on the EC2 instance.
2. CloudWatch collected CPU utilization metrics.
3. The target tracking policy detected that utilization was above its target.
4. The policy requested additional capacity.
5. The Auto Scaling Group launched more EC2 instances, up to the maximum capacity of three.

**Scale-in sequence:**

1. The stress test ended after its configured duration.
2. CPU utilization decreased.
3. CloudWatch collected the lower CPU metrics.
4. The target tracking policy determined that excess capacity could be removed.
5. The Auto Scaling Group terminated excess instances.
6. The group retained one instance because its minimum capacity was one.

## 8. Important concepts

| Term | Explanation |
|---|---|
| Auto Scaling Group | A collection of EC2 instances that AWS manages as a group. |
| Launch Template | A reusable configuration that defines how new EC2 instances should be launched. |
| Minimum capacity | The smallest number of instances the ASG should maintain. |
| Desired capacity | The number of instances the ASG currently aims to maintain. |
| Maximum capacity | The largest number of instances the ASG is allowed to launch. |
| Scale-out | Increasing the number of instances when demand rises. |
| Scale-in | Decreasing the number of instances when demand falls. |
| Target tracking | A scaling policy that adjusts capacity to keep a selected metric near a target value. |
| CloudWatch | AWS monitoring service used to collect metrics and evaluate alarms. |
| Instance warmup | A period allowed for a newly launched instance to initialize before its metrics are fully considered by scaling decisions. |
| Session Manager | An AWS Systems Manager feature that provides managed access to an EC2 instance without requiring inbound SSH access. |

## 9. Observations and result

The practical was completed successfully.

| Stage | Observed result |
|---|---|
| Initial state | Auto Scaling Group maintained one healthy EC2 instance. |
| High CPU workload | `stress-ng` increased CPU utilization. |
| Scale-out | The Auto Scaling Group automatically launched additional instances. |
| Workload ended | CPU utilization dropped after the stress test stopped. |
| Scale-in | The Auto Scaling Group automatically terminated excess instances. |
| Final state | The group returned to one healthy instance, respecting the minimum capacity. |

**Result:** An AWS Auto Scaling Group was configured successfully with a target tracking policy based on average CPU utilization. Dynamic provisioning was observed under high workload, and automatic scale-in was observed after the workload decreased.

## 10. Screenshots to include in the practical record

Capture screenshots from your own AWS Console to document the configuration and results:

1. Launch Template details showing `CC-Lab-Template`.
2. Auto Scaling Group details showing `CC-Lab-ASG`, minimum capacity 1, desired capacity 1, and maximum capacity 3.
3. Scaling policy showing target tracking, average CPU utilization, target 30%, and 120-second warmup.
4. EC2 or ASG instance list during scale-out, showing the additional instances.
5. ASG Activity history showing successful instance launch activities.
6. EC2 or ASG instance list after scale-in, showing one remaining healthy instance.
7. ASG Activity history showing successful termination activities.

Use screenshots from the actual run. Do not create or edit screenshots to imply a state that was not observed.

## 11. Troubleshooting notes

### Session Manager cannot connect

- Check that the EC2 instance has the `CC-Lab-SSM-Role` IAM role attached.
- Check that the role has the `AmazonSSMManagedInstanceCore` policy.
- Check that the instance has outbound network connectivity.
- Wait for the instance to obtain credentials and register with Systems Manager. Rebooting and waiting resolved the initial registration issue during this practical.

### CPU load increases but the ASG does not scale out immediately

- Confirm that the target tracking policy is enabled.
- Confirm that the metric is average CPU utilization and the target is 30%.
- Check the ASG Activity history and CloudWatch alarms.
- Allow time for metric collection, alarm evaluation, and instance warmup.

### Instances do not terminate immediately after CPU drops

- Confirm that the `stress-ng` process has stopped using `pgrep -af stress-ng`.
- Check that scale-in is enabled in the target tracking policy.
- Check the ASG Activity history for scaling events or errors.
- Allow time for CloudWatch evaluation and AWS scaling stabilization.
- Remember that the ASG will not scale below its minimum capacity of one.

## 12. Conclusion

In this practical, an AWS Auto Scaling Group was created using an EC2 launch template. A target tracking policy was configured to maintain average CPU utilization around 30%. CPU load was generated using `stress-ng` through an AWS Systems Manager Session Manager terminal. When CPU utilization increased, the Auto Scaling Group automatically launched additional EC2 instances. After the workload ended and CPU utilization decreased, the group automatically terminated excess instances and returned to one healthy instance. This demonstrated dynamic provisioning and automatic capacity adjustment in AWS.
