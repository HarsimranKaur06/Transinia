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
  count = var.create_vpc_resources ? 1 : 0
  
  cidr_block = var.vpc_cidr
  tags       = merge(local.tags, { Name = "${local.app}-${local.env}-vpc" })
}

# Data source to fetch existing VPC if not creating one
data "aws_vpc" "existing" {
  count = var.create_vpc_resources ? 0 : 1
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-vpc"]
  }
}

# Local value to use either the created VPC or the data source
locals {
  vpc_id = var.create_vpc_resources ? aws_vpc.main[0].id : data.aws_vpc.existing[0].id
}

resource "aws_internet_gateway" "igw" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id = local.vpc_id
  tags   = merge(local.tags, { Name = "${local.app}-${local.env}-igw" })
}

# PUBLIC SUBNETS (2) — pinned to first two standard AZs
resource "aws_subnet" "public_a" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id                  = local.vpc_id
  cidr_block              = local.public_cidrs[0]
  availability_zone       = local.azs_std[0]
  map_public_ip_on_launch = true
  tags                    = merge(local.tags, { Name = "${local.app}-${local.env}-subnet-public-a" })
}

resource "aws_subnet" "public_b" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id                  = local.vpc_id
  cidr_block              = local.public_cidrs[1]
  availability_zone       = local.azs_std[1]
  map_public_ip_on_launch = true
  tags                    = merge(local.tags, { Name = "${local.app}-${local.env}-subnet-public-b" })
}

# Data sources to fetch existing subnets if not creating them
data "aws_subnet" "public_a" {
  count = var.create_vpc_resources ? 0 : 1
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-subnet-public-a"]
  }
}

data "aws_subnet" "public_b" {
  count = var.create_vpc_resources ? 0 : 1
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-subnet-public-b"]
  }
}

# Local values for subnet IDs
locals {
  public_subnet_a_id = var.create_vpc_resources ? aws_subnet.public_a[0].id : data.aws_subnet.public_a[0].id
  public_subnet_b_id = var.create_vpc_resources ? aws_subnet.public_b[0].id : data.aws_subnet.public_b[0].id
}

resource "aws_route_table" "public" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id = local.vpc_id
  tags   = merge(local.tags, { Name = "${local.app}-${local.env}-rt-public" })
}

data "aws_route_table" "public" {
  count = var.create_vpc_resources ? 0 : 1
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-rt-public"]
  }
}

locals {
  public_route_table_id = var.create_vpc_resources ? aws_route_table.public[0].id : data.aws_route_table.public[0].id
}

resource "aws_route" "public_igw" {
  count = var.create_vpc_resources ? 1 : 0
  
  route_table_id         = local.public_route_table_id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = var.create_vpc_resources ? aws_internet_gateway.igw[0].id : null
}

resource "aws_route_table_association" "public_assoc_a" {
  count = var.create_vpc_resources ? 1 : 0
  
  subnet_id      = local.public_subnet_a_id
  route_table_id = local.public_route_table_id
}

resource "aws_route_table_association" "public_assoc_b" {
  count = var.create_vpc_resources ? 1 : 0
  
  subnet_id      = local.public_subnet_b_id
  route_table_id = local.public_route_table_id
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
