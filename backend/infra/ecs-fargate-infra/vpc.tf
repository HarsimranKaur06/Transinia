# Only standard availability zones (exclude Local Zones / Wavelength)
data "aws_availability_zones" "standard" {
  state = "available"

  # Standard AZs don't require opt-in
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }

  # Ensure we don't pick Local Zones
  filter {
    name   = "zone-type"
    values = ["availability-zone"]
  }
}

locals {
  azs_std       = slice(data.aws_availability_zones.standard.names, 0, 2) # pick first two standard AZs
  public_cidrs  = var.public_subnet_cidrs
  private_cidrs = var.private_subnet_cidrs
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = merge(local.tags, { Name = "${local.app}-${local.env}-vpc" })
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = merge(local.tags, { Name = "${local.app}-${local.env}-igw" })
}

# PUBLIC SUBNETS (2) — pinned to first two standard AZs
resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_cidrs[0]
  availability_zone       = local.azs_std[0]
  map_public_ip_on_launch = true
  tags                    = merge(local.tags, { Name = "${local.app}-${local.env}-public-1" })
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_cidrs[1]
  availability_zone       = local.azs_std[1]
  map_public_ip_on_launch = true
  tags                    = merge(local.tags, { Name = "${local.app}-${local.env}-public-2" })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags   = merge(local.tags, { Name = "${local.app}-${local.env}-public-rt" })
}

resource "aws_route" "public_igw" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_assoc_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_assoc_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

# NAT for private subnets — place NAT GW in a STANDARD AZ public subnet
resource "aws_eip" "nat" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]
  tags       = merge(local.tags, { Name = "${local.app}-${local.env}-nat-eip" })
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_a.id
  tags          = merge(local.tags, { Name = "${local.app}-${local.env}-nat" })
}

# PRIVATE SUBNETS (2) — pinned to the same two standard AZs
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_cidrs[0]
  availability_zone = local.azs_std[0]
  tags              = merge(local.tags, { Name = "${local.app}-${local.env}-private-1" })
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_cidrs[1]
  availability_zone = local.azs_std[1]
  tags              = merge(local.tags, { Name = "${local.app}-${local.env}-private-2" })
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  tags   = merge(local.tags, { Name = "${local.app}-${local.env}-private-rt" })
}

resource "aws_route" "private_nat" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat.id
}

resource "aws_route_table_association" "private_assoc_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_assoc_b" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private.id
}
