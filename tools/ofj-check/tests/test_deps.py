import unittest

from ofjcheck import deps

UBUNTU = 'NAME="Ubuntu"\nID=ubuntu\nID_LIKE=debian\nPRETTY_NAME="Ubuntu 24.04.2 LTS"\n'
FEDORA = 'NAME="Fedora Linux"\nID=fedora\n'
WSL_KERNEL = "Linux version 5.15.167.4-microsoft-standard-WSL2"


class DepsTest(unittest.TestCase):
    def test_platform_detection(self):
        plat = deps.detect_platform(os_release=UBUNTU, proc_version=WSL_KERNEL)
        self.assertEqual((plat.system, plat.distro_id, plat.wsl), ("Linux", "ubuntu", True))
        self.assertEqual(plat.label, "ubuntu (WSL)")
        self.assertFalse(deps.detect_platform(os_release=FEDORA, proc_version="Linux 6.8").wsl)

    def test_install_commands(self):
        pkgs = {"apt": "git", "dnf": "git", "generic": "git"}
        ubuntu = deps.detect_platform(os_release=UBUNTU, proc_version="")
        fedora = deps.detect_platform(os_release=FEDORA, proc_version="")
        other = deps.detect_platform(os_release="ID=gentoo\n", proc_version="")
        self.assertEqual(deps.system_install_command(ubuntu, pkgs), "sudo apt install git")
        self.assertEqual(deps.system_install_command(fedora, pkgs), "sudo dnf install git")
        self.assertIn("package manager", deps.system_install_command(other, pkgs))

    def test_python_package_hint_mentions_venv_packages_when_missing(self):
        ubuntu = deps.detect_platform(os_release=UBUNTU, proc_version=WSL_KERNEL)
        if deps.in_virtualenv():
            self.skipTest("hint differs inside a virtualenv")
        hint = deps.python_package_hint(ubuntu, venv_available=False)
        self.assertEqual(hint[0], "sudo apt install python3-venv python3-pip")
        self.assertTrue(any("pip install -r" in h for h in hint))
        self.assertNotIn("python3-venv", " ".join(deps.python_package_hint(ubuntu, True)))

    def test_check_dependencies(self):
        statuses = deps.check_dependencies(need_pdf=False)
        names = [s.name for s in statuses]
        self.assertEqual(names[0], "Python")
        self.assertIn("git", names)
        pdf = statuses[-1]
        self.assertFalse(pdf.required)
        self.assertTrue(statuses[0].ok)
        text = deps.format_status(statuses)
        self.assertIn("Environment:", text)


if __name__ == "__main__":
    unittest.main()
