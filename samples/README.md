# Test videos

Put parking-lot videos for testing and demos in this folder, e.g. `samples/parking_demo.mp4`.
Video files here are not committed to git (see `.gitignore`), so large or shared clips stay on
your machine.

To run on a video instead of the webcam, set this in `config.py`:

```python
VIDEO_SOURCE = "samples/parking_demo.mp4"
```

Then mark the spots for that video (`python spot_marker.py`) and run `python main.py`.
Each camera angle or video needs its own spots, so delete `parking_spots.json` and
`reference_frame.jpg` before marking spots for a different video.
