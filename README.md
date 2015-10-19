# foolaunch

## Command-Line Usage

	usage: foolaunch [option]* <cfg>
	Options and arguments:
	  -p, --profile <arg>          : aws credentials profile
	  -r, --region <arg>           : aws region
	  --image <arg>                : ami image name
	  -t, --instance-type <arg>    : ec2 instance type
	  --placement <arg>            : ec2 availability zone
	  --subnet <arg>               : vpc subnet name
	  --key <arg>                  : ec2 key pair name
	  --instance-profile <arg>     : iam instance profile name
	  --security-groups <arg>      : ec2 security group names (comma separated)
	  --tags <arg>                 : instance tags as JSON string
	  --root-volume-size <arg>     : root volume size in GB
	  --load-balancers <arg>       : load balancer names (comma separated)
	  --user-data-file <arg>       : file containing instance user data
	  --spot, --no-spot            : use spot pricing (or not)
	  --dry-run                    : dry run
	  --name <arg>                 : ec2 instance name
	  -n, --count <arg>            : number of instances to launch
	  --price <arg>                : max price
