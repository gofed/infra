#!/usr/bin/python

from ansible.module_utils.basic import *
import time
import datetime

def main():

    fields = {
        "coverage": {"required": True, "type": "list"},
        "from_ts": {"required": False, "type": "str"},
        "from_date": {"required": False, "type": "str"},
        "to_ts": {"required": False, "type": "str"},
        "to_date": {"required": False, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    from_ts = 0
    if module.params["from_ts"]:
        from_ts = int(module.params["from_ts"])
    elif module.params["from_date"]:
        from_ts = int(time.mktime(datetime.datetime.strptime(module.params["from_date"], "%Y-%m-%d").timetuple()))

    if module.params["to_ts"]:
        to_ts = int(module.params["to_ts"])
    elif module.params["to_date"]:
        to_ts = int(time.mktime(datetime.datetime.strptime(module.params["to_date"], "%Y-%m-%d").timetuple()))
    else:
        to_ts = int(time.time())

    from_m = int(datetime.datetime.fromtimestamp(from_ts).strftime("%m"))
    from_y = int(datetime.datetime.fromtimestamp(from_ts).strftime("%Y"))
    to_m = int(datetime.datetime.fromtimestamp(to_ts).strftime("%m"))
    to_y = int(datetime.datetime.fromtimestamp(to_ts).strftime("%Y"))

    coverage = {}
    for item in module.params["coverage"]:
        try:
            ditem = datetime.datetime.strptime(item, "%Y-%m-%d %H:%M")
        except ValueError:
            ditem = datetime.datetime.strptime(item, "%Y-%m")

        y = int(ditem.year)
        m = int(ditem.month)
        if y not in coverage:
            coverage[y] = {}
        coverage[y][m] = item

    covered = True
    while True:
        if from_y not in coverage:
            covered=False
            break
        if from_m not in coverage[from_y]:
            covered=False
            break

        if from_y == to_y and from_m == to_m:
            break

        from_m += 1
        if from_m == 13:
            from_m = 1
            from_y +=1

    # Find the biggest year
    b_y = sorted(coverage.keys())[-1]
    # Find the biggest month
    b_m = sorted(coverage[b_y].keys())[-1]

    c_y = int(datetime.datetime.now().year)
    c_m = int(datetime.datetime.now().month)

    # any day in the coverage date?
    if c_y == b_y and c_m == b_m:
        if len(coverage[c_y][c_m]) > 10:
            ditem = datetime.datetime.strptime(coverage[c_y][c_m], "%Y-%m-%d %H:%M")
            end_ts = int(time.mktime(ditem.timetuple()))
            if to_ts > end_ts:
                covered=False

    result = dict(
        changed=True,
        covered=covered,
        tested={
            "since": datetime.datetime.fromtimestamp(from_ts).strftime('%Y-%m-%d %H:%M:%S'),
            "to": datetime.datetime.fromtimestamp(to_ts).strftime('%Y-%m-%d %H:%M:%S'),
        }
    )

    module.exit_json(**result)

if __name__ == '__main__':
    main()
