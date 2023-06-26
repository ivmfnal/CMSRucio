
# NOTE: Maybe this should be run from somewhere where the team has access? 
# It is running in an acrontab owned by Benedict Maier

from rucio.client import Client
client = Client()

# ddm_quota are weight given to RSEs based on the amount of free space
# This is calulated as static use - rucio use
# The rule evaluation algorithm uses a weighted random selection of RSEs based on this value

# NOTE: This probably needs to be reviewed after an assement of age of dynamic data at different sites
# and if this can be used to normalise that


DRY_RUN = True

# Adding ddm_quota attribute to all disk RSEs
# T3s do not have the "static" usage set, they are quasi-static
RSE_EXPRESSION = "rse_type=DISK&cms_type=real&tier<3&tier>0"

rses = [rse["rse"] for rse in client.list_rses(rse_expression=RSE_EXPRESSION)]

for rse in rses:
    rse_usage = list(client.get_rse_usage(rse))

    static, rucio = 0, 0

    for source in rse_usage:
        if source["source"] == "static":
            static = source["used"]
        if source["source"] == "rucio":
            rucio = source["used"]

    ddm_quota = max(static - rucio, 0)
 
    # Override ddm_quota for operational purposes
    rse_attributes = client.list_rse_attributes(rse)
    if "override_ddm_quota" in rse_attributes:
        ddm_quota = rse_attributes["override_ddm_quota"]
    
    if not DRY_RUN:
        client.add_rse_attribute(rse, "ddm_quota", ddm_quota)
    print("Setting ddm_quota for {} to {}".format(rse, ddm_quota))
