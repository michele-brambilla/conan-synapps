import os

from conans import AutoToolsBuildEnvironment, ConanFile, RunEnvironment, tools


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

    no_modules = ["ALIVE", "CAMAC", "CAPUTRECORDER", "DAC128V", "DELAYGEN", "DXP", "DXPSITORO", "DEVIOCSTATS", "IP", "IPAC", "IP330", "IPUNIDIG", "LOVE", "LUA", "MCA", "MEASCOMP", "MODBUS", "MOTOR", "OPTICS", "QUADEM", "SOFTGLUE", "SOFTGLUEZYNQ", "STD", "VAC", "VME", "YOKOGAWA_DAS", "XXX", "STREAM", "AREA_DETECTOR", "ADCORE", "ADSUPPORT", "ADSIMDETECTOR", "ALLEN_BRADLEY"]
    modules = []

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

    def _comment_unwanted_modules(self):
        for module in self.no_modules:
            tools.replace_in_file("synApps/support/configure/RELEASE", module, "# "+module)

    def _list_wanted_modules(self):
        prefix='=$(SUPPORT)/'
        modules=[]
        with open("synApps/support/configure/RELEASE") as f:
            for line in f:
                if prefix in line and line[0] != '#':
                    modules.append(os.path.basename(line.rstrip()))
        return modules

    def build(self):
        epics_base, _ = self.get_epics_info()

        # set options
        tools.replace_in_file("synApps/support/configure/CONFIG_SITE", "LINUX_USB_INSTALLED = YES", "LINUX_USB_INSTALLED = NO")
        tools.replace_in_file("synApps/support/configure/CONFIG_SITE", "LINUX_NET_INSTALLED = YES", "LINUX_NET_INSTALLED = NO")

        # replace EPICS paths
        tools.replace_in_file("synApps/support/configure/RELEASE", "SUPPORT=/home/oxygen40/KLANG/Documents/synApps/support", "SUPPORT="+os.getcwd()+"/synApps/support")
        tools.replace_in_file("synApps/support/configure/RELEASE", "EPICS_BASE=/APSshare/epics/base-3.15.5", "EPICS_BASE="+epics_base)


        autotools = AutoToolsBuildEnvironment(self)
        env_build = RunEnvironment(self)

        self._comment_unwanted_modules()
        self.modules = self._list_wanted_modules()

        # propagate changes
        with tools.chdir('synApps/support'):
            autotools.make(target='release',vars=env_build.vars)
            autotools.make(vars=env_build.vars)


    def package(self):
        if tools.os_info.is_linux:
            arch = "linux-x86_64"
        elif tools.os_info.is_macos:
            arch = "darwin-x86"

        for module in self.modules:
            path = os.path.join('synApps/support',module,'lib',arch)
            if os.path.isdir(path):
                print(os.listdir(path))

#        base_lib_dir = os.path.join(os.cwd(), 'synApps/support')
#        for f in os.listdir():
#            self.copy("*.a", dst="lib", src=f,keep_path=False)
#
            #        # Package EPICS Base
#        base_bin_dir = os.path.join(EPICS_BASE_DIR, "bin", arch)
#        for b in EPICS_BASE_BINS:
#            self.copy(b, dst="bin", src=base_bin_dir)
#        self.copy("*.dll", dst="bin", src=base_bin_dir)
#        self.copy("*", dst="include", src=os.path.join(EPICS_BASE_DIR, "include"),
#                  excludes="valgrind/*", keep_path=False)
#        self.copy("*", dst="lib", src=os.path.join(EPICS_BASE_DIR, "lib", arch))
#        self.copy("pkgconfig/*", dst="lib", src=os.path.join(EPICS_BASE_DIR, "lib"))

#        # Package EPICS V4
#        for d in EPICS_V4_SUBDIRS:
#            self.copy("*", dst="include", src=os.path.join(EPICS_V4_DIR, d, "include"))
#            self.copy("*", dst="lib", src=os.path.join(EPICS_V4_DIR, d, "lib", arch))
#            self.copy("*.dll", dst="bin", src=os.path.join(EPICS_V4_DIR, d, "bin", arch))
#        v4_bin_dir = os.path.join(EPICS_V4_DIR, "pvAccessCPP", "bin", arch)
#        for b in EPICS_V4_BINS:
#            self.copy(b, dst="bin", src=v4_bin_dir)
#
#        self.copy("LICENSE.*")
#
#    def package(self):
#        with tools.chdir('synApps/support'):
#            print('PWD: %r'%os.listdir())
#            for f in os.listdir():
#                try:
#                    with tools.chdir(f+'/lib/darwin-x86'):
#                        print('\tFILES: %r'%os.listdir())
#                        self.copy("*.dylib", dst="lib", src=".")
#                except Exception as e:
#                    pass
#            self.copy("lib*.dylib", dst="lib", src="*/lib/darwin-x86/")
#            self.copy("*.h", dst="include",src="*/include")
#            self.copy("*/lib/darwin-x86/lib*.lib", dst="lib")
#            self.copy("*/lib/darwin-x86/lib*.so", dst="lib")
#            self.copy("*/lib/darwin-x86/lib*.dylib", dst="lib")
#            self.copy("*/lib/darwin-x86/lib*.a", dst="lib")

#   def package_info(self):
#       self.cpp_info.libs = [self.name]
#
