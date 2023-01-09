# SPDX-License-Identifier: LGPL-2.1+

import subprocess
import urllib.request
from typing import Set

from mkosi.backend import MkosiState, add_packages
from mkosi.distributions.debian import DebianInstaller,invoke_apt


class PopInstaller(DebianInstaller):
    repositories_for_boot = {"universe"}

    @classmethod
    def _add_default_kernel_package(cls, state: MkosiState, extra_packages: Set[str]) -> None:
        # use the global metapckage linux-generic if the user didn't pick one
        if ("linux-system76" not in extra_packages and
            not any(package.startswith("linux-image") for package in extra_packages)):
            add_packages(state.config, extra_packages, "linux-system76")

    @classmethod
    def _add_apt_auxiliary_repos(cls, state: MkosiState, repos: Set[str]) -> None:
        if state.config.release in ("unstable", "sid"):
            return

        updates = f"deb {state.config.mirror} {state.config.release}-updates {' '.join(repos)}"
        state.root.joinpath(f"etc/apt/sources.list.d/{state.config.release}-updates.list").write_text(f"{updates}\n")

        # Security updates repos are never mirrored
        security = f"deb http://security.ubuntu.com/ubuntu/ {state.config.release}-security {' '.join(repos)}"
        state.root.joinpath(f"etc/apt/sources.list.d/{state.config.release}-security.list").write_text(f"{security}\n")

        main = f"deb [signed-by=/usr/share/keyrings/pop-archive-keyring.gpg] http://apt.pop-os.org/release {state.config.release} main"
        state.root.joinpath(f"etc/apt/sources.list.d/{state.config.release}-main-pop.list").write_text(f"{main}\n")

        proprietary = f"deb [signed-by=/usr/share/keyrings/pop-archive-keyring.gpg] http://apt.pop-os.org/proprietary {state.config.release} main"
        state.root.joinpath(f"etc/apt/sources.list.d/{state.config.release}-proprietary-pop.list").write_text(f"{proprietary}\n")

        urllib.request.urlretrieve("http://keyserver.ubuntu.com/pks/lookup?op=get&search=0x63c46df0140d738961429f4e204dd8aec33a7aff", state.root.joinpath("usr/share/keyrings/pop-archive-keyring.gpg"))
        invoke_apt(state, "key", "add", ["/usr/share/keyrings/pop-archive-keyring.gpg"], stdout=subprocess.PIPE).stdout.strip()

    @classmethod
    def _fixup_resolved(cls, state: MkosiState, extra_packages: Set[str]) -> None:
        pass
