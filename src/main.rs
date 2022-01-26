use std::time::Duration;
use structopt::StructOpt;
use std::path::PathBuf;
use std::io::Write;
use log::{error, info};

mod utils;
use utils::{Experiment, Result};

#[derive(StructOpt)]
struct Opt {
    #[structopt(long)]
    n_peers: usize,

    #[structopt(long, default_value = "1", help = "unit: bytes")]
    payload_size: usize,

    #[structopt(long, default_value = "1000", help = "warming up time of subscribers")]
    warmup: u64,

    #[structopt(long, default_value = "5000", help = "timeout of receiving messages")]
    timeout: u64,

    #[structopt(long, default_value = "output", help = "output directory for storing exp log")]
    output_dir: PathBuf,
}


#[async_std::main]
async fn main() ->Result<()> {
    let Opt {
        n_peers,
        payload_size,
        warmup,
        timeout,
        output_dir
    } = Opt::from_args();

    pretty_env_logger::init();
    let warmup = Duration::from_millis(warmup);
    let timeout = Duration::from_millis(timeout) + warmup;
    let exp = Experiment {
        n_peers,
        payload_size,
        warmup,
        timeout,
    };

    match exp.run().await {
        Ok(exp_log) => {
            std::fs::create_dir_all(&output_dir)?;
            let mut file = std::fs::File::create(&output_dir.join("result.json"))?;
            writeln!(&mut file, "{}", serde_json::to_string_pretty(&exp_log)?)?;
            info!("Exp {}-{} succeeded", &n_peers, &payload_size);
        }
        Err(_) => {
            error!("Exp {}-{} failed.", &n_peers, &payload_size);
        }
    };
    Ok(())
}
