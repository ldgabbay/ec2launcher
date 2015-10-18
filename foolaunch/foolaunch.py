# -*- coding: utf-8 -*-

import os
import cjson
import time

import boto
import boto.ec2
import boto.ec2.blockdevicemapping
import boto.ec2.elb
import boto.s3
import boto.vpc

r"""
This script simplifies the process to spawn instances on EC2 built from scratch
on top of Amazon's original AMI.

There are two parts to this task. The first is to create the instance, and the
second is to apply patches to it.


Part 1: Create the instance

A few things are needed:
* authentication (profile or keys)
* region (e.g. us-east-1)
* image name (amzn-2015.09...)
* virtualization type (hvm, pv)
* instance type (e.g. m1.small)
* destination (availability zone or subnet id)
* role
* security groups

Ideally, a few tweaks are:
* automatically attach block devices
* (optionally) use spot pricing
* add to load balancer
* set tags
* set root volume size
* set key


"""


EC2_INSTANCE_INFO = {
    "t2.micro": {"price": 0.013, "num_block_devices": 0},
    "t1.micro": {"price": 0.02, "num_block_devices": 0},
    "t2.small": {"price": 0.026, "num_block_devices": 0},
    "m1.small": {"price": 0.044, "num_block_devices": 1},
    "t2.medium": {"price": 0.052, "num_block_devices": 0},
    "m3.medium": {"price": 0.067, "num_block_devices": 1},
    "m1.medium": {"price": 0.087, "num_block_devices": 1},
    "t2.large": {"price": 0.104, "num_block_devices": 0},
    "c3.large": {"price": 0.105, "num_block_devices": 2},
    "c4.large": {"price": 0.11, "num_block_devices": 0},
    "m4.large": {"price": 0.126, "num_block_devices": 0},
    "c1.medium": {"price": 0.13, "num_block_devices": 1},
    "m3.large": {"price": 0.133, "num_block_devices": 1},
    "r3.large": {"price": 0.175, "num_block_devices": 1},
    "m1.large": {"price": 0.175, "num_block_devices": 2},
    "c3.xlarge": {"price": 0.21, "num_block_devices": 2},
    "c4.xlarge": {"price": 0.22, "num_block_devices": 0},
    "m2.xlarge": {"price": 0.245, "num_block_devices": 1},
    "m4.xlarge": {"price": 0.252, "num_block_devices": 0},
    "m3.xlarge": {"price": 0.266, "num_block_devices": 2},
    "r3.xlarge": {"price": 0.35, "num_block_devices": 1},
    "m1.xlarge": {"price": 0.35, "num_block_devices": 4},
    "c3.2xlarge": {"price": 0.42, "num_block_devices": 2},
    "c4.2xlarge": {"price": 0.441, "num_block_devices": 0},
    "m2.2xlarge": {"price": 0.49, "num_block_devices": 1},
    "m4.2xlarge": {"price": 0.504, "num_block_devices": 0},
    "c1.xlarge": {"price": 0.52, "num_block_devices": 4},
    "m3.2xlarge": {"price": 0.532, "num_block_devices": 2},
    "g2.2xlarge": {"price": 0.65, "num_block_devices": 1},
    "d2.xlarge": {"price": 0.69, "num_block_devices": 3},
    "r3.2xlarge": {"price": 0.7, "num_block_devices": 1},
    "c3.4xlarge": {"price": 0.84, "num_block_devices": 2},
    "i2.xlarge": {"price": 0.853, "num_block_devices": 1},
    "c4.4xlarge": {"price": 0.882, "num_block_devices": 0},
    "m2.4xlarge": {"price": 0.98, "num_block_devices": 2},
    "m4.4xlarge": {"price": 1.008, "num_block_devices": 0},
    "d2.2xlarge": {"price": 1.38, "num_block_devices": 6},
    "r3.4xlarge": {"price": 1.4, "num_block_devices": 1},
    "c3.8xlarge": {"price": 1.68, "num_block_devices": 2},
    "i2.2xlarge": {"price": 1.705, "num_block_devices": 2},
    "c4.8xlarge": {"price": 1.763, "num_block_devices": 0},
    "cc2.8xlarge": {"price": 2, "num_block_devices": 4},
    "cg1.4xlarge": {"price": 2.1, "num_block_devices": 2},
    "m4.10xlarge": {"price": 2.52, "num_block_devices": 0},
    "g2.8xlarge": {"price": 2.6, "num_block_devices": 2},
    "d2.4xlarge": {"price": 2.76, "num_block_devices": 12},
    "r3.8xlarge": {"price": 2.8, "num_block_devices": 2},
    "hi1.4xlarge": {"price": 3.1, "num_block_devices": 2},
    "i2.4xlarge": {"price": 3.41, "num_block_devices": 4},
    "cr1.8xlarge": {"price": 3.5, "num_block_devices": 2},
    "hs1.8xlarge": {"price": 4.6, "num_block_devices": 24},
    "d2.8xlarge": {"price": 5.52, "num_block_devices": 24},
    "i2.8xlarge": {"price": 6.82, "num_block_devices": 8}
}


DEVICE_LETTER = []

for i in xrange(1, 26):
    DEVICE_LETTER.append(chr(ord('a')+i))
for i in xrange(0, 26):
    for j in xrange(0, 26):
        DEVICE_LETTER.append(chr(ord('a')+i) + chr(ord('a')+j))


def make_block_device_map(image, instance_type, root_volume_size=None):
    import boto.ec2.blockdevicemapping

    block_device_mapping = boto.ec2.blockdevicemapping.BlockDeviceMapping()

    if root_volume_size and (image.block_device_mapping['/dev/xvda'].size != root_volume_size):
        root_volume = boto.ec2.blockdevicemapping.BlockDeviceType()
        root_volume.size = root_volume_size
        block_device_mapping['/dev/xvda'] = root_volume

    for i in xrange(EC2_INSTANCE_INFO[instance_type]["num_block_devices"]):
        block_device_mapping['/dev/sd' + DEVICE_LETTER[i]] = \
            boto.ec2.blockdevicemapping.BlockDeviceType(ephemeral_name="ephemeral{}".format(i))

    if len(block_device_mapping) > 0:
        return block_device_mapping
    return None


def lookup_ami_id(ec2, name):
    """Returns AMI id for `name`"""

    images = ec2.get_all_images(filters={'name': [name]})
    if len(images) != 1:
        raise RuntimeError('cannot find exactly one image')
    return images[0]


def lookup_security_group_ids(ec2, names):
    if not names:
        return None
    return [x.id for x in ec2.get_all_security_groups(filters={'group_name': names})]


class Configuration(object):
    def __init__(self):
        # aws profile name
        self.profile = None
        # aws region name
        self.region = None
        # ami image name
        self.image = None
        # ec2 instance type
        self.instance_type = None
        # ec2 availability zone
        self.placement = None
        # subnet id
        self.subnet = None
        # key pair name
        self.key = None
        # iam instance profile name
        self.instance_profile = None
        # security group names (list)
        self.security_groups = None
        # instance tags to set (dict (str->str))
        self.tags = None
        # root volume size (number, in ??)
        self.root_volume_size = None
        # elastic load balancers (list (str))
        self.load_balancers = None
        # instance user data (str)
        self.user_data_b64 = None
        # use spot pricing
        self.spot = False
        # dry run
        self.dry_run = False
        # instance name
        self.name = None
        # number of instances to launch
        self.count = None
        # max price
        self.price = None

    def apply_configuration(self, configuration):
        if not isinstance(configuration, dict):
            raise ValueError()
        # TODO make this more robust
        valid_keys = {
                "profile",
                "region",
                "image",
                "instance_type",
                "placement",
                "subnet",
                "key",
                "instance_profile",
                "security_groups",
                "tags",
                "root_volume_size",
                "load_balancers",
                "user_data_b64",
                "spot",
                "name",
                "count",
                "price"
            }
        for k, v in configuration.iteritems():
            if k not in valid_keys:
                raise ValueError()
            setattr(self, k, v)


class Connections(object):
    def __init__(self):
        self.ec2 = None
        self.vpc = None
        self.elb = None


class Context(object):
    def __init__(self):
        self.image = None
        self.image_id = None
        self.block_device_mapping = None
        self.security_group_ids = None
        self.subnet_id = None


def launch(cfg):
    conn = Connections()

    conn.ec2 = boto.ec2.connect_to_region(cfg.region, profile_name=cfg.profile)
    conn.vpc = boto.vpc.connect_to_region(cfg.region, profile_name=cfg.profile)
    conn.elb = boto.ec2.elb.connect_to_region(cfg.region, profile_name=cfg.profile)

    ctx = Context()

    print "connected"

    # -- find ami image id --

    ctx.image = lookup_ami_id(conn.ec2, cfg.image)
    ctx.image_id = ctx.image.id

    print "ami image '{}' found as '{}'".format(cfg.image, ctx.image_id)

    # -- find placement or subnet id --

    if cfg.subnet:
        subnets = [s for s in conn.vpc.get_all_subnets() if ("Name" in s.tags) and (s.tags["Name"] == cfg.subnet)]
        if subnets:
            if len(subnets) > 1:
                raise ValueError("too many matching subnets")
            ctx.subnet_id = subnets[0].id
        print "subnet '{}' found as '{}'".format(cfg.subnet, ctx.subnet_id)

    # -- create block device mapping --

    ctx.block_device_mapping = make_block_device_map(ctx.image, cfg.instance_type, cfg.root_volume_size)

    # -- find security group ids --

    ctx.security_group_ids = lookup_security_group_ids(conn.ec2, cfg.security_groups)

    create_kwargs = {
        'instance_type': cfg.instance_type,
        'dry_run': cfg.dry_run
    }

    if ctx.subnet_id:
        create_kwargs['subnet_id'] = ctx.subnet_id
    elif cfg.placement:
        create_kwargs['placement'] = cfg.placement

    if cfg.key:
        create_kwargs['key_name'] = cfg.key

    if cfg.instance_profile:
        create_kwargs['instance_profile_name'] = cfg.instance_profile

    if ctx.security_group_ids:
        create_kwargs['security_group_ids'] = ctx.security_group_ids

    if ctx.block_device_mapping:
        create_kwargs['block_device_map'] = ctx.block_device_mapping

    if cfg.user_data_b64:
        create_kwargs['user_data'] = cfg.user_data_b64

    instance_ids = []
    if cfg.spot:
        if cfg.count:
            create_kwargs['count'] = cfg.count

        price = EC2_INSTANCE_INFO[cfg.instance_type]["price"]
        if cfg.price:
            price = cfg.price

        result = conn.ec2.request_spot_instances(price, ctx.image_id, **create_kwargs)
        spot_request_ids = [x.id for x in result]
        for spot_request_id in spot_request_ids:
            state = 'open'
            while state == 'open':
                print "Waiting on spot request..."
                time.sleep(5)
                spot = conn.ec2.get_all_spot_instance_requests(spot_request_id)[0]
                state = spot.state
            if state != 'active':
                print "Failed to create instance."
                continue
            instance_ids.append(spot.instance_id)
    else:
        if cfg.count:
            create_kwargs['min_count'] = cfg.count
            create_kwargs['max_count'] = cfg.count
        
        result = conn.ec2.run_instances(ctx.image_id, **create_kwargs)
        for i in result.instances:
            instance_ids.append(i.id)

    if instance_ids:
        print "Instances '{}' created.".format(', '.join(instance_ids))

        if cfg.name:
            conn.ec2.create_tags([i for i in instance_ids], {"Name": cfg.name}, dry_run=cfg.dry_run)

        if cfg.tags:
            conn.ec2.create_tags([i for i in instance_ids], cfg.tags, dry_run=cfg.dry_run)

        if not cfg.dry_run and cfg.load_balancers:
            for load_balancer in cfg.load_balancers:
                conn.elb.register_instances(load_balancer, [i for i in instance_ids])

        reservations = conn.ec2.get_all_instances(instance_ids)
        instances = [i for r in reservations for i in r.instances]
        for i in instances:
            print "{}: {}".format(i.id, i.ip_address)

        return conn, instances

    return conn, []
