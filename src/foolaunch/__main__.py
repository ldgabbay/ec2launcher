#!/usr/bin/env pipenv-python

import sys
import os
import getopt
import base64
import ujson

import foolaunch


def usage(*args):
    if args:
        print("{0}: {1}".format(os.path.basename(sys.argv[0]), args[0]), file=sys.stderr)
    print("usage: {0} [option]* <cfg>".format(os.path.basename(sys.argv[0])), file=sys.stderr)
    print("Options and arguments:", file=sys.stderr)
    print("  -p, --profile <arg>          : aws credentials profile", file=sys.stderr)
    print("  -r, --region <arg>           : aws region", file=sys.stderr)
    print("  --image-filters <arg>        : ami filters", file=sys.stderr)
    print("  -t, --instance-type <arg>    : ec2 instance type", file=sys.stderr)
    print("  --placement <arg>            : ec2 availability zone", file=sys.stderr)
    print("  --subnet <arg>               : vpc subnet name", file=sys.stderr)
    print("  --key <arg>                  : ec2 key pair name", file=sys.stderr)
    print("  --instance-profile <arg>     : iam instance profile name", file=sys.stderr)
    print("  --security-groups <arg>      : ec2 security group names (comma separated)", file=sys.stderr)
    print("  --tags <arg>                 : instance tags as JSON string", file=sys.stderr)
    print("  --root-volume-size <arg>     : root volume size in GB", file=sys.stderr)
    print("  --load-balancers <arg>       : load balancer names (comma separated)", file=sys.stderr)
    print("  --user-data-file <arg>       : file containing instance user data", file=sys.stderr)
    print("  --spot, --no-spot            : use spot pricing (or not)", file=sys.stderr)
    print("  --dry-run                    : dry run", file=sys.stderr)
    print("  --name <arg>                 : ec2 instance name", file=sys.stderr)
    print("  -n, --count <arg>            : number of instances to launch", file=sys.stderr)
    print("  --price <arg>                : max price", file=sys.stderr)
    sys.exit(1)


def parse_command_line(cfg):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:r:t:n:", [
            "profile=",
            "region=",
            "image-filters=",
            "instance-type=",
            "placement=",
            "subnet=",
            "key=",
            "instance-profile=",
            "security-groups=",
            "tags=",
            "root-volume-size=",
            "load-balancers=",
            "user-data-file=",
            "spot",
            "no-spot",
            "dry-run",
            "name=",
            "count=",
            "price="
        ])
    except getopt.GetoptError as err:
        usage("bad option")

    if len(args) < 1:
        usage("missing configuration name")

    cfg.apply(args[0])

    for opt, arg in opts:
        if opt in ('-p', '--profile'):
            cfg.profile = arg
        elif opt in ('-r', '--region'):
            cfg.region = arg
        elif opt == '--image-filters':
            cfg.image_filters = ujson.loads(arg)
        elif opt in ('-t', '--instance-type'):
            cfg.instance_type = arg
        elif opt == '--placement':
            cfg.placement = arg
        elif opt == '--subnet':
            cfg.subnet = arg
        elif opt == '--key':
            cfg.key = arg
        elif opt == '--instance-profile':
            cfg.instance_profile = arg
        elif opt == '--security-groups':
            cfg.security_groups = arg.split(',')
        elif opt == '--tags':
            cfg.tags = ujson.loads(arg)
        elif opt == '--root-volume-size':
            cfg.root_volume_size = int(arg)
        elif opt == '--load-balancers':
            cfg.load_balancers = arg.split(',')
        elif opt == '--user-data-file':
            with open(arg, 'rb') as in_file:
                cfg.user_data = in_file.read()
        elif opt == '--spot':
            cfg.spot = True
        elif opt == '--no-spot':
            cfg.spot = False
        elif opt == '--dry-run':
            cfg.dry_run = True
        elif opt == '--name':
            cfg.name = arg
        elif opt in ('-n', '--count'):
            cfg.count = int(arg)
        elif opt == '--price':
            cfg.price = float(arg)
        else:
            assert False


def main():
    try:
        cfg = foolaunch.Session()
        parse_command_line(cfg)
        cfg.launch()
    except Exception as e:
        usage(e)


if __name__ == "__main__":
    main()
