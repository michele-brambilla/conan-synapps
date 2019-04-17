from conans import ConanFile, RunEnvironment, tools, AutoToolsBuildEnvironment
import os

class SynAppsConan(ConanFile):
    name = "synapps"
    version = "0.1"
    license = "<Put the package license here>"
    url = "https://epics.anl.gov/bcda/synApps/tar/synApps_6_0.tar.gz"
    description = "<Description of synApps here>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "gcc"
    requires = 'epics/3.16.1-4.6.0-dm6@ess-dmsc/stable','re2c/0.1@devel/epics'

    def get_epics_info(self):
        epics_base = self.deps_cpp_info["epics"].rootpath.replace('/package/','/build/')

        epics_version = [folder for folder in os.listdir(path=epics_base) if folder.startswith('base-') ]
        if epics_version:
            epics_base+='/'+epics_version[0]
            epics_version = epics_version[0].split('-')[1]
            return epics_base, epics_version
        return ('','')

    def get_module_info(self,modulename):
        result = None
        try:
            result = self.deps_cpp_info[modulename]
        except Exception as e:
            print(e)
        return result

    def source(self):
        self.run("curl -o synApp.tgz "+self.url)
        self.run("tar -xzvf synApp.tgz")

    def build(self):
        epics_base, _ = self.get_epics_info()

        tools.replace_in_file("synApps/support/configure/CONFIG_SITE", "LINUX_USB_INSTALLED = YES", "LINUX_USB_INSTALLED = NO")
        tools.replace_in_file("synApps/support/configure/CONFIG_SITE", "LINUX_NET_INSTALLED = YES", "LINUX_NET_INSTALLED = NO")

        # replace EPICS paths
        tools.replace_in_file("synApps/support/configure/RELEASE", "SUPPORT=/home/oxygen40/KLANG/Documents/synApps/support", "SUPPORT="+os.getcwd()+"/synApps/support")
        tools.replace_in_file("synApps/support/configure/RELEASE", "EPICS_BASE=/APSshare/epics/base-3.15.5", "EPICS_BASE="+epics_base)

        autotools = AutoToolsBuildEnvironment(self)
        env_build = RunEnvironment(self)

        with tools.chdir('synApps/support'):
            autotools.make(target='release',vars=env_build.vars)

        no_modules = ["ALIVE", "CAMAC", "CAPUTRECORDER", "DAC128V", "DELAYGEN", "DXP", "DXPSITORO", "DEVIOCSTATS", "IP", "IPAC", "IP330", "IPUNIDIG", "LOVE", "LUA", "MCA", "MEASCOMP", "MODBUS", "MOTOR", "OPTICS", "QUADEM", "SOFTGLUE", "SOFTGLUEZYNQ", "STD", "VAC", "VME", "YOKOGAWA_DAS", "XXX", "STREAM", "AREA_DETECTOR", "ADCORE", "ADSUPPORT", "ADSIMDETECTOR", "ALLEN_BRADLEY"]
        for module in no_modules:
            tools.replace_in_file("synApps/support/configure/RELEASE", module, "# "+module)

        with tools.chdir('synApps/support'):
            autotools.make(vars=env_build.vars)

    def package(self):
        with tools.chdir('synApps/support'):
            self.copy("*/include/*.h", dst="include")
            self.copy("*/lib/darwin-x86/*.lib", dst="lib")
            self.copy("*/lib/darwin-x86/*.so", dst="lib")
            self.copy("*/lib/darwin-x86/*.dylib", dst="lib")
            self.copy("*/lib/darwin-x86/*.a", dst="lib")

    def package_info(self):
        self.cpp_info.libs = [self.name]
