ERROR () { printf "ERROR\t%s\n" "$*" >& 2; }
INFO () { printf "INFO\t%s\n" "$*" >& 2; }
DEBUG () { printf "DEBUG\t%s\n" "$*" >& 2; }


OSNAME=$(uname -s)

case $OSNAME in
    darwin)

        # 2025-09-03:
        # *   pyinstaller step is taking 293 sec (=4.9 min) (@GB6=1889)
        #     (John's MacBook Air)
        #
        # *   pyinstaller generates warnings...
        #          797 build/myapp/warn-myapp.txt
        #
        # *   The first execution of dist/app/myapp is slow, compared to
        #     subsequent execution.
        #
        #     14:11:41 		(start)
        #     14:12:04 (00:23)	DEBUG	Added a QueueHandler to root logger.
        #     14:16:28 (04:47)	INFO	The user interface initialized!
        #
        #     14:24:46 		(start)
        #     14:24:47	(00:01)	DEBUG	Added a QueueHandler to root logger.
        #     14:25:15	(00:29)	INFO	The user interface initialized!

        # *   using the --windowed flag automatically creates the
        #     myapp.app bundle in the dist directory, alongside the
        #     myapp executable folder.
        #     There is no separate "conversion" step.

        # *   attribution for the sunflower.png icon downloaded from
        #     flaticon.com:
        #         How to attribute?
        #         Paste this link on the website where your app is
        #         available for download or in the description section
        #         of the platform or marketplace you’re using.
        #         <a href="https://www.flaticon.com/free-icons/sunflower"
        #           title="sunflower icons">Sunflower icons created by
                    Freepik - Flaticon</a>

        # (from pyinstaller.org)
        #   (If you do not specify an icon file, PyInstaller supplies a
        #   file icon-windowed.icns with the PyInstaller logo.)
        #
        #   Use the osx-bundle-identifier= argument to add a bundle
        #   identifier.  This becomes the CFBundleIdentifier used in
        #   code-signing (see the PyInstaller code signing recipe and
        #   for more detail, the Apple code signing overview technical note).
        #
        #   You can add other items to the Info.plist by editing the
        #   spec file; see Spec File Options for a Mac OS X Bundle below.

        set -x

        pyinstaller --windowed \
            --osx-bundle-identifier=yelab.LabGym \
            --icon=sunflower.png \
        \
            --clean --name LabGym \
            --add-data=../logging.yaml:LabGym --noconfirm myapp.py

        # % du -sh dist/*
        # 1.8G	dist/LabGym
        # 1.8G	dist/LabGym.app

        # if you double-click on the sunflower LabGym.app, get LabGym Verifying...
        # the first time only.
        # then UI starts and its tray icon is sunflower.  But no console for logging
        # is created... can't see messages.  :-/

        wc -l build/LabGym/warn-LabGym.txt

        (
            date
            dist/LabGym/LabGym --debug
        )


;;

    *)
        ERROR Unsupported \$OSNAME: $OSNAME
        exit 1
    ;;
esac
