# AmpliconSuite Cross-Version Concordance Environments

一个面向 Linux x86-64 服务器的容器环境，供 [AmpliconSuite Cross-Version Concordance 0.3.0](https://github.com/YenningC/AmpliconSuite-Benchmarks) 使用。镜像把十一个 Suite 版本共用的依赖装好，包含两套隔离 CNVkit、两套 BFBArchitect 和 R/DNAcopy。用户拉取一张镜像后，按步骤准备源码缓存和样本清单即可开始。

> **0.3.0 镜像已发布，支持 Linux x86-64。** 镜像对应更名前的固定源码提交。 GitHub Actions 通过了构建和人工数据组件测试。固定摘要为 `sha256:2273905bd8417cfd2d63af8f25e29c36383b70d2298954ebd834e7ca91959710`。0.2.0 标签仍可供历史 0.2.0 版使用。 [容器包](https://github.com/YenningC/AmpliconSuite-Benchmarks-Environments/pkgs/container/ampliconsuite-benchmarks-environments) · [0.3.0 发布记录](https://github.com/YenningC/AmpliconSuite-Benchmarks-Environments/actions/runs/44042036496)

[English quick start](#english-quick-start) · [第三方许可和组件来源](THIRD_PARTY.md) · [仓库维护者发布步骤](#维护者发布镜像)

## 你需要什么

- Linux x86-64 服务器上的 Docker。Docker Desktop 也可尝试 `--platform linux/amd64`，在 ARM 主机上会使用仿真，当前未在该组合上验证。
- 使用主程序代码前，向其权利人取得书面许可。镜像内装的是运行依赖。`bootstrap` 会从原仓库单独下载固定版本代码。
- 只比较已有结果时需要两套可配对的结果及已知版本。有 BAM 的重跑还需要排序 BAM 和现成索引、已有种子 BED、参考 FASTA/索引、AA 数据资源、背景区段，以及所选 CNV 参考策略的输入。参见 [主程序示例与输入说明](https://github.com/YenningC/AmpliconSuite-Benchmarks#two-input-modes)。
- 若要运行早于 Suite 1.6.2 的 AA，见下方 Mosek 说明。仅比较已有结果或仅跑 AC 无需 Mosek。

## 第一次使用

已发布镜像沿用 `ampliconsuite-benchmarks-environments` 地址。

以下命令在 Bash 中执行。可直接拉取已发布的 0.3.0 镜像，也可按文末说明构建本地镜像。使用新的 `cache-0.3`，让两个发行版的源码缓存各自独立。

```bash
IMAGE=ghcr.io/yenningc/ampliconsuite-benchmarks-environments:0.3.0
mkdir -p cache-0.3 sources config results

docker pull --platform linux/amd64 "$IMAGE"

run_image() {
  docker run --rm --platform linux/amd64 --user "$(id -u):$(id -g)" \
    -e HOME=/tmp "$@"
}

run_image -v "$PWD/cache-0.3:/cache" "$IMAGE" bootstrap
run_image --network none -v "$PWD/cache-0.3:/cache:ro" \
  -v "$PWD/results:/results" "$IMAGE" asbench demo --out /results/demo
```

打开 `results/demo/report.md`。这是人工结果示例，用于确认程序和绘图能启动。发布流水线另有真实组件的微型人工测试。

## 比较实际结果

### 只有已有结果

从 `cache-0.3/benchmarks/examples/benchmarks.results_only.json` 复制模板到 `config/sample.json`。填入实际路径和版本。下面使用 `/data` 作为容器中数据路径。根据实际位置替换 `$DATA_DIR`，并在清单中使用容器内路径。

```bash
DATA_DIR=/absolute/path/to/local/data
run_image --network none -v "$PWD/cache-0.3:/cache:ro" \
  -v "$PWD/config:/config:ro" -v "$DATA_DIR:/data:ro" \
  -v "$PWD/results:/results" "$IMAGE" asbench run \
  --manifest /config/sample.json --out /results/existing-results
```

只比较已生成的多版本结果时，上述配置保留 `runtimes: []`。想用其他版本 AC 重分类时，用 `benchmarks.ac_only.json` 作为清单模板，然后执行下面的源码准备和 `configure-runtime`。按该模板挂载匹配的参考资源。

### 有 BAM，需要重跑选定版本

首次准备上游源码。`prepare-panel` 会下载十一个版本所需的去重后 AA/AC 源码，逐一校验哈希。也可加 `--versions suite-1.6.2` 仅准备参考版，其他目标按需加到列表中。

```bash
run_image -v "$PWD/cache-0.3:/cache:ro" -v "$PWD/sources:/sources" \
  "$IMAGE" prepare-panel
```

从 `cache-0.3/benchmarks/examples/benchmarks.with_bam.json` 复制模板为 `config/sample.json`。输入路径可使用 `/data/...`，参考路径使用 `/reference/...`。先试参考版时，选用已有 Suite 1.6.2 结果的样本可以同时检查来源复现。其他来源版本要评估来源复现，须纳入对应重跑版本。

```bash
run_image --network none -v "$PWD/cache-0.3:/cache:ro" \
  -v "$PWD/sources:/sources:ro" -v "$PWD/config:/config" \
  "$IMAGE" configure-runtime --input /config/sample.json --out /config/run.json \
  --versions suite-1.6.2

DATA_DIR=/absolute/path/to/local/data
REFERENCE_DIR=/absolute/path/to/local/reference
run_benchmark() {
  run_image --network none -v "$PWD/cache-0.3:/cache:ro" \
    -v "$PWD/sources:/sources:ro" -v "$PWD/config:/config:ro" \
    -v "$DATA_DIR:/data:ro" -v "$REFERENCE_DIR:/reference:ro" \
    -v "$PWD/results:/results" "$IMAGE" asbench "$@"
}
run_benchmark check --manifest /config/run.json --out /results/benchmark
run_benchmark run --manifest /config/run.json --out /results/benchmark
```

`configure-runtime` 依据清单的 `target_versions` 选择版本。如希望显式配置全部十一个，删除清单中的 `target_versions` 字段并省略命令中的 `--versions`。它保留固定参考、区分两代 AC/BFB 依赖，并按锁映射两个 CNVkit 版本。缺少某版依赖时，原程序会记录失败或不可用状态。同一清单和输出目录可续跑。查看 `/results/benchmark/report.md` 和运行状态，区分有结果的版本与缺少授权的版本。

### 历史 AA 的 Mosek

| Suite | AA | BFB 环境 | CNVkit | 对 Mosek 的要求 |
|---|---|---|---|---|
| 1.2.2、1.3.3、1.3.4、1.3.7、1.4.0、1.5.0、1.5.2 | 原生 Mosek | 对应旧 AC，无 BFBArchitect 要求 | 0.9.10 | 官方 Python 客户端＋有效许可证 |
| 1.5.3 | 原生 Mosek | AC 1.5.2，无 BFBArchitect 要求 | 0.9.13 | 官方 Python 客户端＋有效许可证 |
| 1.6.0、1.6.1 | Clarabel | BFBArchitect 1.0.1，PuLP 3.3.0 / CBC | 0.9.13 | 上游 AA 启动时导入 Mosek，需客户端。该 AA 的 Clarabel 求解不用 Mosek 许可证 |
| 1.6.2 | Clarabel | BFBArchitect 1.0.2，PuLP 3.3.0 / CBC | 0.9.13 | 无 |

如有使用授权，可以用镜像的一条命令把官方 Mosek Python 发行包装到自己的目录。11.2.8 是开发验证使用的客户端版本，是否能完成求解取决于你的许可证和实际环境。

```bash
mkdir -p mosek-python
run_image -v "$PWD/mosek-python:/sdk" \
  --entrypoint /usr/local/bin/python "$IMAGE" \
  -m pip install --no-deps --target /sdk 'Mosek==11.2.8'
```

生成历史版清单时，在 **镜像名之前**加以下挂载，在 `configure-runtime` **参数中**加对应选项。之后运行 `asbench check` 和 `run` 的容器同样要带这些挂载。仅运行 1.6.0/1.6.1 时可省略许可证挂载和 `--mosek-license`。

| 目的 | Docker 参数 | `configure-runtime` 参数 |
|---|---|---|
| Mosek 客户端 | `-v "$PWD/mosek-python:/mosek-python:ro"` | `--mosek-pythonpath /mosek-python` |
| 个人许可证文件 | `-v "/absolute/path/mosek.lic:/licenses/mosek.lic:ro"` | `--mosek-license /licenses/mosek.lic` |

使用机构浮动许可时按管理员配置传入 `MOSEKLM_LICENSE_FILE`，并允许容器访问许可证服务器。上例的 `--network none` 适用于本地许可证文件和无需联网的分析。许可文件和二进制客户端保留在本地绑定目录。环境镜像使用 CBC 路径。实际求解器选择仍由工具探针和运行记录确认。

## 维护者发布镜像

1. 先把待发布的主程序源码提交到 [主程序仓库](https://github.com/YenningC/AmpliconSuite-Benchmarks) 的 `main`，再更新环境库根目录。提交文件包括 `.github/workflows/environment.yml`、`.dockerignore` 和 `benchmarks-source.lock.json`。0.3.0 的 Dockerfile 固定到已核验的主程序提交。构建会逐一核对源码锁中的 87 个文件后才安装主程序的 Python 依赖。镜像记录通过核验的提交，`bootstrap` 始终下载该提交。
2. 在 **Actions → Build and test the Linux environment** 查看首次构建。它会核验十一版 AC 的源码和启动、两个 BFB/CBC、小型 Clarabel 问题、两版 CNVkit 局部 CBS 和报告示例。真实患者和商业许可证不用于 CI。
3. 首次测试通过后，在同一工作流上点 **Run workflow**，选择默认分支并勾选 `publish`。此时工作流会再次构建、测试，然后用当前仓库的 `GITHUB_TOKEN` 发布到 `ghcr.io/yenningc/ampliconsuite-benchmarks-environments:0.3.0` 和带提交号的标签。运行 Summary 会记录镜像 digest。
4. 若希望别人免登录拉取，在该容器包的设置中确认可见性。代码仓库和容器包各有自己的发布权限。重复分析建议在清单旁记录具体镜像 digest。参见 [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)。

也可在 Docker 构建机执行 `docker build --platform linux/amd64 -t asbench-environment:0.3.0 .`，然后把示例的 `IMAGE` 改为这个本地标签。复现历史构建时可加 `--build-arg BENCHMARKS_COMMIT=<完整提交哈希>`，提交内容仍需通过源码锁校验。`inventory` 命令显示主程序版本、实际提交及源码锁摘要。完整 Python freeze 和 Debian 软件版本保存在镜像的 `/opt/environment-provenance/`。

这套镜像为比较端点固定关键依赖，并记录整个安装环境。它限定 CNVkit CBS，使用共享科学库和 CBC，不用于重现历史官方容器的每一个环境细节。基因组参考资源按项目与样本另行提供。

## English quick start

This environment repository builds one Linux x86-64 container for the eleven locked Suite recipes used by AmpliconSuite Cross-Version Concordance 0.3.0. It installs two isolated CNVkit releases, both BFBArchitect releases, CBC, Clarabel, R/DNAcopy, samtools and bedtools. After a successful publishing run, users pull the image once. `bootstrap` retrieves the pinned program release separately, and `prepare-panel` retrieves and verifies the selected upstream AA/AC sources into a reusable cache. `configure-runtime` generates an `asbench` manifest from your local input template. Follow the Docker commands above.

Request permission from the project's copyright holder before using its code. Historical AA needs the vendor's Mosek client. The oldest eight Suite recipes also need a valid license. AA in Suite 1.6.0 and 1.6.1 uses Clarabel here but still imports the client at startup. Suite 1.6.2 uses Clarabel without the client. Patient inputs, reference files and license files remain in user-provided mounts. GitHub Actions built, tested and published the Linux amd64 image for 0.3.0. The 0.2.0 tag remains available for the historical 0.2.0 release. The Dockerfile pins the published 0.3.0 program commit. The build verifies every locked file, and `bootstrap` reuses that exact commit. Use a new `cache-0.3` directory.
