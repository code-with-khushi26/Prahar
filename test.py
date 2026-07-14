from watchdog_pipeline import run_watchdog_cycle

results = run_watchdog_cycle(limit_per_feed=3)
print(f"Got {len(results)} results")
for r in results:
    print(r["headline"], "-", r["final_flag"])