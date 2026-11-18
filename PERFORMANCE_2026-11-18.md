# AI Usage motion tuning and performance, 2026-11-18

The live preview now uses Shima's existing gentle cubic curve, with nominal
durations of 360 ms for quota fills, 380 ms for numbers and 180 ms for fades.
Previous values were 280, 300 and 150 ms. The increase is about 80 ms for the
main transitions. Theme speed and reduced-motion settings still apply.

The preview remains uncommitted and unpushed. Both source copies pass all
233 tests without skips, including agent-switch isolation, animation
retargeting, first-value handling, hidden surfaces and reduced motion.

## Measurement method

Host: Ryzen 5 5600, 12 logical CPUs, approximately 31.3 GiB RAM, AMD Radeon
RX 6700, 1920x1080 monitor at 144 Hz. The isolated probe used the real Qt/OpenGL
renderer on Wayland, confirmed by its Mesa/AMD renderer log, not software
rendering. The temporary overlay did not request keyboard focus and exited
after measurement. Only the normal shell instance remains running.

The probe instantiated the actual metric, quota-row and numeric-transition
components with isolated style/service stubs. It compared instant updates,
the previous preview and the smoother candidate, twice in reverse order.
Each run warmed up, settled idle, updated all four values once per second
for eight seconds, then hid the scene while updates continued.

One update per second is 15 times the dashboard's normal 15-second collection
interval. CPU figures below use the usual process convention: 100% means one
logical CPU fully occupied. GPU figures use the process's DRM graphics-engine
time. Frame-swap intervals are client submission intervals, measured with
millisecond timestamps; they are not end-to-end input latency or proof that
the client presents every physical monitor refresh.

## Controlled rendering results

Means across two runs during the one-update-per-second phase:

| Mode | CPU, percent of one core | GPU graphics-engine utilization | Renderer RSS | p95 frame-swap interval | Maximum interval |
| --- | ---: | ---: | ---: | ---: | ---: |
| Instant | 0.19% | 0.016% | 248.5 MiB | 8 ms | 8 ms |
| Previous motion | 1.99% | 0.412% | 246.2 MiB | 8 ms | 9 ms |
| Smoother motion | 2.49% | 0.513% | 246.6 MiB | 8 ms | 9 ms |

The smoother runs produced 880 measured animation frame intervals, versus
704 for the shorter previous motion. Neither had intervals longer than
14 ms. Frame pacing did not regress in this test. The longer duration does
more frames, with a small corresponding increase in CPU work.

Idle and hidden phases had no ongoing animations, no measured graphics-engine
work and CPU usage below the process-tick resolution during the three-second
measurement windows. Hidden data changes snapped without rendering a tween.
This is a short measurement, not a long-term memory-leak test.

RSS differences between profiles were within ordinary process/driver variation.
The approximately 0.4 MiB difference between previous and smoother means does
not establish a causal memory increase. There is no evidence of a substantial
RAM cost from the revision.

### Estimate at the normal collection interval

Subtracting instant-update work and scaling from one update per second to one
per 15 seconds gives a representative animation-only average of approximately:

- **0.154% of one core**, or **0.013% of the 12-thread CPU total**.
- **0.033% graphics-engine utilization**.
- The extra CPU from making the existing motion slightly longer is about
  **0.033 percentage points of one core**, or **0.003% of total CPU**.

These are estimates from the representative card scene. The full Shima bar's
glass effects, other widgets and compositor are not reproduced by that isolated
scene. Multiple real windows, refresh frequency, system load and GPU clocks can
change actual cost. Unchanged collector values do not start new tweens.

## Real shell and whole-system samples

Ten-second samples of the actual shell were taken before and after installation.
The prior shell had been running for over four hours; installation restarted
it. Their memory difference must not be presented as a saving caused by this
change. Background application load was not controlled, so these samples show
the real shell's scale rather than a causal animation-only comparison.

The final candidate sample, after the isolated probes had exited:

| State | Full shell CPU, one-core convention | Shell RSS | Shell GPU graphics-engine time | Compositor CPU, one-core convention | Whole-system CPU |
| --- | ---: | ---: | ---: | ---: | ---: |
| Island closed | 4.17% | 655.8 MiB | 0.71% | 3.77% | 2.99% |
| Desktop/AI Usage open | 15.79% | 690.6 MiB | 26.88% | 5.17% | 4.90% |

The open shell's 15.79% process CPU is approximately 1.32% of this machine's
total 12-thread CPU capacity. Whole-system GPU busy averaged 27.53% in the
open sample, and approximately 25 GiB RAM remained available. The earlier open
shell samples ranged around 18-19% of one core and 19-26% GPU engine time.

The full open panel has a much larger baseline rendering cost than the isolated
numeric transitions. Its live GPU figure should not be confused with the
estimated 0.033% animation increment. Existing effects/widgets and background
activity are included in the full-shell samples.

## Conclusion and limits

No new frame-pacing regression or sustained animation work while hidden/idle
was observed. The slightly longer easing has a small measured incremental cost
on this machine. Heavy-game, CPU-saturated and long-duration memory stress
workloads were not tested, so this does not guarantee absence of lag under
every possible workload.

The live widget matches the tested primary source and has no module errors in
the inspected log. Collector/accounting code, refresh cadence, native data,
authentication and desktop channel remain unchanged. No fake values were
written to production caches for measurement.

Backup before this tuning: the path recorded in
`~/.local/share/ryoku/ai-usage-backup/motion-tuning-20261118-134810/`.
Raw host samples, GPU renderer logs, frame intervals, analysis and the probe
script are archived with that backup under `performance/`.
