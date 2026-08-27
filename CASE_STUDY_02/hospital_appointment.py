"""Hospital appointment & department report — core Python only (lists + sets)."""


def build_report(name, req, avail, prev, doc, adoc, emer):
    """Pure computation, no I/O — lets this run without stdin (see _selftest)."""
    r, a, p, e = set(req), set(avail), set(prev), set(emer)

    common = r & a                      # intersection: requested & available
    unavail = r - a                     # difference: requested not available
    old = r & p                         # intersection: requested & previously visited
    em = r & e                          # intersection: requested & emergency
    all_dep = r | a                     # union: every department in play

    # Emergency departments count as available even if the hospital's avail
    # list didn't carry them (e.g. trauma bay opened ad hoc).
    for d in em:
        common.add(d)                   # adding
        unavail.discard(d)              # removing (discard: no error if absent)

    dup = sorted(d for d in set(req) if req.count(d) > 1)   # list.count + set

    common_doctors = set(doc) & set(adoc)

    if em:
        recommended = sorted(em)[0]
        status = "Emergency Appointment"
    elif common:
        recommended = sorted(common)[0]
        status = "Appointment Available"
    else:
        recommended = "No department"
        status = "Appointment Not Available"

    recommended_confirmed = recommended in a   # membership check

    return {
        "name": name,
        "requested": req,
        "available": avail,
        "common": sorted(common),
        "unavailable": sorted(unavail),
        "previous": sorted(old),
        "emergency": sorted(em),
        "duplicates": dup,
        "common_doctors": sorted(common_doctors),
        "all_departments": sorted(all_dep),
        "recommended": recommended,
        "recommended_confirmed": recommended_confirmed,
        "status": status,
    }


def _selftest():
    # ponytail: one static check, not a suite — enough to catch a broken branch
    rpt = build_report(
        "Test", ["ER", "ER", "Cardiology"], ["Cardiology"],
        ["Cardiology"], ["Dr A"], ["Dr A"], ["ER"],
    )
    assert rpt["duplicates"] == ["ER"]
    assert rpt["status"] == "Emergency Appointment"
    assert rpt["recommended"] == "ER"
    assert "Cardiology" in rpt["common"]
    assert "ER" not in rpt["unavailable"]   # override moved it out

    empty = build_report("Nobody", [], ["Cardiology"], [], [], [], [])
    assert empty["status"] == "Appointment Not Available"
    assert empty["recommended"] == "No department"


def main():
    _selftest()

    name = input("Enter patient name: ")
    req = input("Enter requested departments: ").split()
    avail = input("Enter available departments: ").split()
    prev = input("Enter previously visited departments: ").split()
    doc = input("Enter preferred doctors: ").split()
    adoc = input("Enter available doctors: ").split()
    emer = input("Enter emergency departments: ").split()

    print("\nRequested departments:", req)
    print("First department:", req[0] if req else "None")   # indexing
    print("First 2 departments:", req[:2])                  # slicing

    rpt = build_report(name, req, avail, prev, doc, adoc, emer)

    if rpt["recommended"] == "No department":
        note = ""
    elif rpt["recommended_confirmed"]:
        note = " (confirmed in hospital list)"
    else:
        note = " (emergency override)"

    print("\n----- APPOINTMENT REPORT -----")
    print("Patient Name:", rpt["name"])
    print("Requested:", rpt["requested"])
    print("Available:", rpt["available"])
    print("Unavailable:", rpt["unavailable"])
    print("Common:", rpt["common"])
    print("Previous:", rpt["previous"])
    print("Emergency:", rpt["emergency"])
    print("Duplicate Requests:", rpt["duplicates"])
    print("Common Doctors:", rpt["common_doctors"])
    print("All Departments (union):", rpt["all_departments"])
    print("Recommended Department:", rpt["recommended"] + note)
    print("Final Appointment Status:", rpt["status"])


if __name__ == "__main__":
    main()
