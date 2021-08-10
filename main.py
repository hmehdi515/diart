import sources as src
from pipelines import OnlineDiarization
from sinks import OutputBuilder
from pathlib import Path
import argparse

# Define script arguments
parser = argparse.ArgumentParser()
parser.add_argument("source", type=str, help="Path to an audio file | 'microphone'")
parser.add_argument("--step", default=0.5, type=float, help="Source sliding window step")
parser.add_argument("--latency", required=False, type=float, help="System latency")
parser.add_argument("--sample-rate", default=16000, type=int, help="Source sample rate")
parser.add_argument("--tau", default=0.6, type=float, help="Activity threshold tau active")
parser.add_argument("--rho", default=0.3, type=float, help="Speech duration threshold rho update")
parser.add_argument("--delta", default=1.0, type=float, help="Maximum distance threshold delta new")
parser.add_argument("--gamma", default=3, type=float, help="Parameter gamma for overlapped speech penalty")
parser.add_argument("--beta", default=10, type=float, help="Parameter beta for overlapped speech penalty")
parser.add_argument("--max-speakers", default=20, type=int, help="Maximum number of identifiable speakers")
args = parser.parse_args()

# Manage audio source
uri = args.source
if args.source != "microphone":
    args.source = Path(args.source).expanduser()
    uri = args.source.name
else:
    print("Microphone input is not supported yet")
    exit(1)

# Simulate an unreliable recording protocol yielding new audio with a varying refresh rate
unreliable_source = src.UnreliableFileAudioSource(
    file=args.source,
    uri=uri,
    sample_rate=args.sample_rate,
    refresh_rate_range=(0.1, 1.0),
    simulate_delay=True,
)

# Define online speaker diarization pipeline
pipeline = OnlineDiarization(
    step=args.step,
    latency=args.latency,
    tau_active=args.tau,
    rho_update=args.rho,
    delta_new=args.delta,
    gamma=args.gamma,
    beta=args.beta,
    max_speakers=args.max_speakers,
)

# Configure output builder to write an RTTM file and to draw in real time
output_builder = OutputBuilder(args.source.parent / "output.rttm")
# Build pipeline from audio source and stream results to the output builder
pipeline.from_source(unreliable_source).subscribe(output_builder)
# Read audio source as a stream
unreliable_source.read()