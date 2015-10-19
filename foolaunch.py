#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
import os
import getopt
import base64
import cjson

import foo.launch


def usage():
    print >> sys.stderr, "usage: {0} [option]*".format(os.path.basename(sys.argv[0]))
    print >> sys.stderr, "Options and arguments:"
    print >> sys.stderr, "  -p, --profile <arg>          : aws credentials profile"
    print >> sys.stderr, "  -r, --region <arg>           : aws region"
    print >> sys.stderr, "  --image <arg>                : ami image name"
    print >> sys.stderr, "  -t, --instance-type <arg>    : ec2 instance type"
    print >> sys.stderr, "  --placement <arg>            : ec2 availability zone"
    print >> sys.stderr, "  --subnet <arg>               : vpc subnet name"
    print >> sys.stderr, "  --key <arg>                  : ec2 key pair name"
    print >> sys.stderr, "  --instance-profile <arg>     : iam instance profile name"
    print >> sys.stderr, "  --security-groups <arg>      : ec2 security group names (comma separated)"
    print >> sys.stderr, "  --tags <arg>                 : instance tags as JSON string"
    print >> sys.stderr, "  --root-volume-size <arg>     : root volume size in GB"
    print >> sys.stderr, "  --load-balancers <arg>       : load balancer names (comma separated)"
    print >> sys.stderr, "  --user-data-file <arg>       : file containing instance user data"
    print >> sys.stderr, "  --spot, --no-spot            : use spot pricing (or not)"
    print >> sys.stderr, "  --dry-run                    : dry run"
    print >> sys.stderr, "  --name <arg>                 : ec2 instance name"
    print >> sys.stderr, "  -n, --count <arg>            : number of instances to launch"
    print >> sys.stderr, "  --price <arg>                : max price"
    sys.exit(1)


def parse_command_line(cfg):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:r:t:n:", [
            "profile=",
            "region=",
            "image=",
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
        print >> sys.stderr, err
        usage()

    for opt, arg in opts:
        if opt in ('-p', '--profile'):
            cfg.profile = arg
        elif opt in ('-r', '--region'):
            cfg.region = arg
        elif opt == '--image':
            cfg.image = arg
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
            cfg.tags = cjson.decode(arg)
        elif opt == '--root-volume-size':
            cfg.root_volume_size = int(arg)
        elif opt == '--load-balancers':
            cfg.load_balancers = arg.split(',')
        elif opt == '--user-data-file':
            with open(arg, 'r') as in_file:
                cfg.user_data_b64 = base64.b64encode(in_file.read())
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
    cfg = foo.launch.Session()
    parse_command_line(cfg)
    cfg.launch()


if __name__ == "__main__":
    main()
