"""
Test data that can be used for testing new code or analyses.
"""

#_cue_timepoints = [[12.39, 23.74, 45.74, 67.84, 89.83], [3.12, 54.02, 78.93]]
#_cue_durations = [[6.75, 7.84, 5.48, 4.34, 6.04], [5.29, 7.93, 8.92]]
#_touch_timepoints = [[15.34, 29.43, 68.31], [55.49, 80.85]]
#_resets_timepoints = [
#    [16.34, 17.43, 31.84, 70.84], [1.12, 1.52, 18.01, 30.01, 88.29]
#]
#_spont_reach_timepoints = [[1.43, 1.69], [18.32, 31.12, 88.45]]
#_cued_lift_timepoints = [[15.19, 29.13, 68.03], [55.21, 80.43]]
#
#data = dict(
#    # config settings and metadata
#    duration=1234,
#    spout_count=2,
#    reward_duration_ms=10000,
#    iti=[1000, 2000],
#    json_path='/path/to/json/files',
#    start_time=1000000000.0000000,
#    end_time=1000001234.0000000,
#    date='2000-01-01',
#    notes='Hakuna matata',
#    # data
#    cue_timepoints=_cue_timepoints,
#    cue_durations=_cue_durations,
#    touch_timepoints=_touch_timepoints,
#    resets_timepoints=_resets_timepoints,
#    spont_reach_timepoints=_spont_reach_timepoints,
#    cued_lift_timepoints=_cued_lift_timepoints,
#)



trials = [
    start=03.12, spout=0, shaping=1, cue_duration=5.29, spout_position=3, outcome=0, end=8.41,
    start=12.39, spout=1, shaping=0, cue_duration=6.75, spout_position=3, outcome=1, end=12.,
    start=23.74, spout=0, shaping=1, cue_duration=7.84, spout_position=3, outcome=1, end=,
    start=45.74, spout=1, shaping=1, cue_duration=5.48, spout_position=3, outcome=2, end=,
    start=54.02, spout=0, shaping=1, cue_duration=7.93, spout_position=3, outcome=0, end=61.95,
    start=67.84, spout=1, shaping=1, cue_duration=4.34, spout_position=3, outcome=1, end=,
    start=78.93, spout=1, shaping=1, cue_duration=8.92, spout_position=4, outcome=2, end=,
    start=89.83, spout=0, shaping=0, cue_duration=6.04, spout_position=4, outcome=1, end=,
    LIFTS
    END

]

data = dict(
    # config settings and metadata
    duration=1234,
    spout_count=2,
    iti=[1000, 2000],
    json_path='/path/to/json/files',
    start_time=1000000000.0000000,
    end_time=1000001234.0000000,
    date='2000-01-01',
    notes='Hakuna matata',
    # data
    trials=_trials,
    resets=(),
    spontaneous_reaches=(),
)
