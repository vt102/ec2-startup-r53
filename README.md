# EC2 Startup Route53

A simple solution to set a route53 DNS CNAME to whatever IP address a "pet" server comes up as.

## Prereqs

This project assumes the following:
* python 3 installed
* aws command line utility installed and configured
* systemd is used to start services on boot

## Installing:

1. Create instance profile by launching cfn/instance-profile.yaml
    ```
    aws cloudformation create-stack --template-body file://cfn/instance-profile.yaml --stack-name Route53Profile --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=Domain,ParameterValue=aws.example.com
    ```
1. Get the name of the newly created profile
   ```
   aws cloudformation describe-stacks --stack-name Route53Profile | jq -r '.Stacks[] | select(.StackName=="Route53Profile") | .Outputs[] | select(.OutputKey=="ProfileName") | .OutputValue'
   ```
1. Associate the instance profile with the EC2 instance (or launch new instance with the profile)
   ```
   aws ec2 associate-iam-instance-profile --instance-id i-0123456789abcfef0 --iam-instance-profile Name=aws.example.com-R53Access-Profile
   ```
1. Set up your host to run update_r53.py on boot (this is on ubuntu).
    ```
    $ sudo cp update_r53.py /usr/local/bin
    $ sudo cp ec2-startup-r53.service /etc/systemd/system
    $ sudo systemctl enable ec2-startup-r53
    Created symlink from /etc/systemd/system/multi-user.target.wants/ec2-startup-r53.service to /etc/systemd/system/ec2-startup-r53.service.
    $
    ```
