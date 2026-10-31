# Assignment 5: Migrate a Local Virtual Machine to AWS

This document is a **reproduction guide** for completing the practical
from the beginning. Follow the steps in order to export a local Ubuntu
VM from VirtualBox, import it into AWS, launch an EC2 instance, and test
access.

> **Recorded outcome from this practical:** The Ubuntu image was
> successfully imported and an EC2 instance was launched. SSH access was
> not established. The troubleshooting section records what was tried
> and what remained unresolved.

## 1. Prerequisites

Before starting, make sure you have:

-   A working Ubuntu virtual machine in Oracle VM VirtualBox.
-   An AWS account with permission to use IAM, S3, VM Import/Export, and
    EC2.
-   AWS CloudShell available in the AWS Console.
-   A local computer with Windows PowerShell and the OpenSSH client.
-   Enough time to upload an image of approximately 5 GB.

Use the same AWS Region for the S3 bucket, image import, and EC2
instance. In this practical, the Region was **US East (N. Virginia),
`us-east-1`**.

## 2. Export the Ubuntu VM from VirtualBox

1.  Start Oracle VM VirtualBox.

2.  Select the Ubuntu virtual machine.

3.  Confirm that the VM starts and that the required files are present.

4.  Shut down the guest operating system cleanly. Do not export it while
    it is running.

5.  In VirtualBox, open **File → Export Appliance**.

6.  Select the Ubuntu VM and continue.

7.  Choose the OVA format and save the appliance as:

    `CC-Lab2.ova`

8.  Complete the export.

9.  Keep the OVA file in a convenient folder.

The OVA archive contains the VM configuration and virtual disk. In this
practical, the OVA was also extracted and produced:

`CC-Lab2-disk001.vmdk`

## 3. Create an S3 bucket and upload the VM files

1.  Sign in to the AWS Management Console.

2.  Open **Amazon S3**.

3.  Select **Create bucket**.

4.  Enter this bucket name:

    `cc-lab-vm-migration-assignment5`

5.  Select Region **US East (N. Virginia) `us-east-1`**.

6.  Keep the bucket private and retain the default security settings.

7.  Create the bucket.

8.  Open the bucket and select **Upload**.

9.  Add these files:

    -   `CC-Lab2.ova`
    -   `CC-Lab2-disk001.vmdk`

10. Start the upload and wait for it to finish.

The OVA was approximately 5.06 GB. The import configuration used the OVA
object.

### Verify the OVA from CloudShell

Open CloudShell from the AWS Console and run:

``` bash
aws s3api head-object \
  --bucket cc-lab-vm-migration-assignment5 \
  --key CC-Lab2.ova \
  --region us-east-1
```

The command should return object metadata, including its content length.
In this practical, the content length was `5060959744` bytes.

Check the bucket Region:

``` bash
aws s3api get-bucket-location \
  --bucket cc-lab-vm-migration-assignment5
```

A `null` `LocationConstraint` means the bucket is in `us-east-1`.

## 4. Configure the VM Import/Export IAM role

VM Import/Export needs a service role that it can assume to read the
image from S3 and create the required EC2 resources.

### 4.1 Create or open the `vmimport` role

1.  Open **IAM** in the AWS Console.
2.  Select **Roles**.
3.  Create a role named `vmimport`, or open the existing role if it has
    already been created.
4.  Configure its trust relationship to allow the VM Import/Export
    service to assume it.
5.  Use the following trust policy:

``` json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "vmie.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:Externalid": "vmimport"
        }
      }
    }
  ]
}
```

### 4.2 Attach the role permissions

Create a customer-managed policy named `vmimport-permissions` and attach
it to the `vmimport` role.

Use this policy for the bucket used in this practical:

``` json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::cc-lab-vm-migration-assignment5",
        "arn:aws:s3:::cc-lab-vm-migration-assignment5/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:ModifySnapshotAttribute",
        "ec2:CopySnapshot",
        "ec2:RegisterImage",
        "ec2:Describe*"
      ],
      "Resource": "*"
    }
  ]
}
```

Save the policy and attach it to `vmimport`.

### 4.3 Give the IAM user permission to start the import

The IAM identity used by CloudShell also needs permission to start and
inspect the import and pass the service role.

In this practical, an inline policy named `VMImportUserPermissions` was
attached to the CloudShell IAM user. Its policy was:

``` json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:ImportImage",
        "ec2:DescribeImportImageTasks",
        "ec2:CancelImportTask"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketLocation",
        "s3:ListBucket",
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::cc-lab-vm-migration-assignment5",
        "arn:aws:s3:::cc-lab-vm-migration-assignment5/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::834305733975:role/vmimport"
    }
  ]
}
```

If reproducing this in a different AWS account, replace the account ID
in the role ARN with your own account ID.

### Verify the AWS identity

In CloudShell, run:

``` bash
aws sts get-caller-identity
```

Confirm that the command returns the intended AWS account and IAM
identity.

## 5. Create the import configuration file

In CloudShell, create a file called `containers.json`:

``` bash
nano containers.json
```

Paste the following JSON:

``` json
[
  {
    "Description": "CC Lab 2 Ubuntu VM",
    "Format": "OVA",
    "UserBucket": {
      "S3Bucket": "cc-lab-vm-migration-assignment5",
      "S3Key": "CC-Lab2.ova"
    }
  }
]
```

Save the file. In nano, use **Ctrl+O**, press **Enter**, and then
**Ctrl+X**.

Verify its contents:

``` bash
cat containers.json
```

Make sure the bucket name and object key match the actual S3 bucket and
uploaded OVA file.

## 6. Import the OVA into AWS

Run this command in CloudShell:

``` bash
aws ec2 import-image \
  --description "CC Lab 2 Ubuntu VM Migration" \
  --disk-containers file://containers.json \
  --region us-east-1
```

**Important:** Do not add `--license-type AWS` for this Ubuntu/Linux
import. The first attempt in this practical included that option and
failed with:

``` text
CLIENT_ERROR : License type is incompatible with selected platform
```

The corrected command omitted the explicit license type. AWS then
accepted the import and returned a new import task ID.

Copy the `ImportTaskId` from your own command output. Do not reuse an ID
from an earlier attempt.

## 7. Monitor the import

Use the task ID returned by the previous command:

``` bash
aws ec2 describe-import-image-tasks \
  --import-task-ids YOUR_IMPORT_TASK_ID \
  --region us-east-1
```

Replace `YOUR_IMPORT_TASK_ID` with the actual value.

Run the command again after a short wait if the task is still active.
Wait until the task reports:

``` text
"Status": "completed"
```

A completed task should also provide an AMI ID in the `ImageId` field.

### Result from the completed practical

The successful import returned:

-   Import task: `import-ami-a2141c90d8a74241t`
-   AMI: `ami-05a2207c3431d652a`
-   Snapshot: `snap-08179851b310bce58`
-   Platform: `Linux`
-   Architecture: `x86_64`
-   License type: `BYOL`

Record the AMI ID returned by your own run. It may be different if you
repeat the practical.

## 8. Launch an EC2 instance from the imported AMI

1.  Open **EC2** in the AWS Console.

2.  In the navigation pane, select **AMIs** under **Images**.

3.  Set the ownership filter to **Owned by me**.

4.  Find the AMI created by the import task.

5.  Select it and choose **Launch instance from AMI**.

6.  Set an instance name, for example:

    `CC-Lab2-Migrated-Ubuntu`

7.  Select an instance type compatible with the AMI architecture. The
    imported image in this practical was `x86_64`.

8.  Select or create a key pair. Download the private key file and keep
    it safe.

9.  Select the VPC and subnet for the instance.

10. Ensure the instance has a public IPv4 address if you intend to
    connect to it directly over the internet.

11. Configure or select a security group.

12. Review the storage configuration.

13. Launch the instance.

14. Open the EC2 Instances page and wait for the instance state to
    become **Running**.

The instance created in this practical had these details:

  Setting             Value
  ------------------- ---------------------------
  Name                `CC-Lab2-Migrated-Ubuntu`
  Instance ID         `i-030c6fa828219c7ea`
  Public IPv4         `54.164.99.110`
  Private IPv4        `172.31.29.30`
  Availability Zone   `us-east-1b`

Your instance ID and IP addresses will be different if you repeat the
steps.

## 9. Configure the security group for SSH

1.  Open the instance details page.
2.  Select the **Security** tab.
3.  Open the attached security group.
4.  Select **Edit inbound rules**.
5.  Add an inbound rule with:

  Field        Value
  ------------ -------
  Type         SSH
  Protocol     TCP
  Port range   22
  Source       My IP

6.  Save the rules.

In this practical, the source was `49.36.48.179/32`. Use your current
public IP instead of copying this address. You can check it in Windows
PowerShell:

``` powershell
curl.exe https://checkip.amazonaws.com
```

If your public IP changes, update the security group rule to match it.
Do not leave SSH open to everyone unless there is a specific, temporary
reason.

## 10. Connect using SSH

On Windows, open PowerShell in the folder containing your downloaded
`.pem` key file.

For an Ubuntu image, try the `ubuntu` username:

``` powershell
ssh -i ".\cc-lab-migration-key.pem" ubuntu@YOUR_PUBLIC_DNS
```

Replace `YOUR_PUBLIC_DNS` with the Public IPv4 DNS shown on the EC2
instance details page.

For the instance created in this practical, the DNS name was:

``` text
ec2-54-164-99-110.compute-1.amazonaws.com
```

The corresponding command was:

``` powershell
ssh -i ".\cc-lab-migration-key.pem" ubuntu@ec2-54-164-99-110.compute-1.amazonaws.com
```

The default username can depend on the image. For Ubuntu cloud images it
is commonly `ubuntu`; `root` is generally not the correct initial login
user.

### If Windows reports that the private key permissions are too open

Run these commands from PowerShell:

``` powershell
icacls.exe ".\cc-lab-migration-key.pem" /inheritance:r
icacls.exe ".\cc-lab-migration-key.pem" /grant:r "$($env:USERNAME):R"
```

Then retry the SSH command.

## 11. Troubleshoot SSH if the connection fails

A key distinction:

-   **Connection timed out** usually means the client cannot reach the
    host and port.
-   **Connection refused** means the host was reached, but the
    connection was actively rejected or no service was accepting
    connections on that port.
-   **Permission denied (publickey)** means the SSH service was reached,
    but authentication failed.

Follow these checks in order.

### 11.1 Confirm the public IP

``` powershell
curl.exe https://checkip.amazonaws.com
```

Make sure the returned address matches the source address in the
security group's SSH inbound rule.

### 11.2 Test port 22

``` powershell
Test-NetConnection YOUR_PUBLIC_DNS -Port 22
```

Look for:

``` text
TcpTestSucceeded : True
```

If it is `False`, SSH is not reachable from the computer.

### 11.3 Check the AWS security group

Confirm that:

-   The SSH rule is inbound.
-   The protocol is TCP.
-   The port is 22.
-   The source is your current public IP with `/32`.
-   The security group is attached to the correct EC2 instance.

### 11.4 Check EC2 status checks

On the EC2 instance page, open **Status and alarms**. Check:

-   System status check
-   Instance status check
-   Attached EBS status check

Passing checks indicate that AWS's infrastructure and instance
reachability checks passed. They do not prove that the SSH daemon inside
the guest operating system is running.

### 11.5 Try EC2 Instance Connect

1.  Select the EC2 instance.
2.  Choose **Connect**.
3.  Open the **EC2 Instance Connect** tab.
4.  Select the public IP option if applicable.
5.  Enter the appropriate operating-system username, commonly `ubuntu`
    for Ubuntu.
6.  Select **Connect**.

Instance Connect still needs a reachable SSH service and suitable
network configuration. It is not a way to bypass a guest that is not
accepting SSH connections.

### 11.6 Systems Manager and Serial Console alternatives

-   **Systems Manager Session Manager:** The instance must be configured
    as a managed node, including the required agent, IAM permissions and
    network access. If it does not appear in Fleet Manager, it is not
    currently available through this route.
-   **EC2 Serial Console:** The AWS account and instance must support
    and be authorized for this feature. Account-level authorization may
    need to be enabled first.

If these options are unavailable, a more involved recovery procedure may
be required, such as stopping the instance, attaching its root EBS
volume to a helper instance, and inspecting or repairing the guest
operating system. This was not performed in the recorded practical.

## 12. Actual Outcome of This Practical

The following stages were completed:

-   Ubuntu VM exported from VirtualBox as an OVA.
-   OVA and extracted VMDK uploaded to S3.
-   IAM role and required permissions configured.
-   OVA imported successfully using VM Import/Export.
-   AMI and EBS snapshot created.
-   EC2 instance launched from the imported AMI.
-   System, instance and EBS status checks passed.

The following stages were **not** completed:

-   SSH login to the migrated Ubuntu VM.
-   Verification of the Ubuntu shell after migration.
-   Verification of the original files and applications from inside the
    EC2 instance.

In the recorded attempt, SSH returned `Connection refused`, and
`Test-NetConnection` reported `TcpTestSucceeded: False`. EC2 Instance
Connect also failed. The exact guest-level cause was not confirmed. A
missing, inactive or incorrectly configured SSH service was a
possibility, but it was not verified.

## 13. Cleanup and Cost Control

When the practical is complete:

1.  Stop the EC2 instance if it is no longer needed temporarily.
2.  Remember that stopping an instance does not delete its EBS volumes.
3.  EBS volumes and snapshots may continue to incur storage charges.
4.  The imported AMI's backing snapshot and the S3 objects may also
    incur storage charges.
5.  Retain the AMI, snapshot and S3 files if they are needed for
    evaluation.
6.  Terminate the instance and delete other resources only when you are
    certain they are no longer required.

## 14. Quick Command Checklist

Commands used during the practical:

``` bash
# Check the AWS identity
aws sts get-caller-identity

# Check the bucket's Region
aws s3api get-bucket-location \
  --bucket cc-lab-vm-migration-assignment5

# Verify the OVA object
aws s3api head-object \
  --bucket cc-lab-vm-migration-assignment5 \
  --key CC-Lab2.ova \
  --region us-east-1

# View the import configuration
cat containers.json

# Start the import (do not add --license-type AWS)
aws ec2 import-image \
  --description "CC Lab 2 Ubuntu VM Migration" \
  --disk-containers file://containers.json \
  --region us-east-1

# Monitor the import (replace with your task ID)
aws ec2 describe-import-image-tasks \
  --import-task-ids YOUR_IMPORT_TASK_ID \
  --region us-east-1
```

Windows PowerShell commands:

``` powershell
# Check the current public IP
curl.exe https://checkip.amazonaws.com

# Test SSH connectivity (replace the DNS name)
Test-NetConnection YOUR_PUBLIC_DNS -Port 22

# Connect to the Ubuntu instance (replace DNS and key path)
ssh -i ".\cc-lab-migration-key.pem" ubuntu@YOUR_PUBLIC_DNS
```

------------------------------------------------------------------------

**End of reproduction guide.**
