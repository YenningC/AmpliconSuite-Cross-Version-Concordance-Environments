# Software sources and permissions

This is an environment for research use. Use of AmpliconSuite Cross-Version Concordance itself is governed by [the project's permission notice](https://github.com/YenningC/AmpliconSuite-Cross-Version-Concordance/blob/main/LICENSE_STATUS.md). The container does not contain its checkout or change the project's permission terms. `bootstrap` obtains the pinned checkout separately from its GitHub repository.

| Component | Source and packaging |
|---|---|
| AmpliconArchitect | Locked source is downloaded separately into the user's cache. The UC terms grant permissions for educational, research and nonprofit purposes, with retained notices. Consult UC for commercial permission. [AA license](https://github.com/AmpliconSuite/AmpliconArchitect/blob/b96c77bbb824/LICENSE) |
| AmpliconClassifier | Exact sources are downloaded into the user's cache. [AC license](https://github.com/AmpliconSuite/AmpliconClassifier/blob/v2.0.1/LICENSE) |
| AmpliconSuite-pipeline | The program lock records component identities. The full pipeline is not installed or invoked by the image. [Suite license](https://github.com/AmpliconSuite/AmpliconSuite-pipeline/blob/v1.6.2/LICENSE) |
| BFBArchitect 1.0.1/1.0.2 | Built from verified locked source snapshots, with BSD notices in the distributions. Gurobi is omitted even though upstream metadata lists the backend. [BFB license](https://github.com/AmpliconSuite/BFBArchitect/blob/v1.0.2/LICENSE) |
| CNVkit 0.9.10/0.9.13 | Installed as exact upstream Python distributions. This environment supports CBS. CNVkit 0.9.10 loads pomegranate at startup. The PyTorch and optional HMM stack is omitted. [CNVkit license](https://github.com/etal/cnvkit/blob/v0.9.13/LICENSE) |
| Mosek, Gurobi | Their installers, libraries and license files are not bundled. The optional setup command installs the Mosek client from the publisher's Python distribution into a user-owned, separately mounted directory. [Mosek license](https://docs.mosek.com/license/license.pdf) · [Gurobi license](https://cdn.gurobi.com/wp-content/uploads/Gurobi-Standard-EULA-Aug-2025.pdf) |
| Debian and Python dependencies | Debian package sources and exact source versions are identified by `/opt/environment-provenance/debian-packages.tsv`. Source packages are available via [Debian Sources](https://sources.debian.org/). Python distribution notices and metadata are retained in the respective site-packages directories. The Python base is pinned to a digest in `Dockerfile`. |

The runtime metadata records the pinned program commit, supported CPU/OS, solver scope and installed package versions. The public image build context only includes runtime scripts and package specifications. The analysis examples mount all user data and licenses outside that context.
