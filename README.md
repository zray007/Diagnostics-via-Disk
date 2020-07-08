# Bio-ID

## Software based quantitative analysis of disk based bio-assays

Work in progress!

## Make a graph of C2 read errors from a CD/DVD

### Requirements

* Linux machine with a CD/DVD/BluRay device. Raspberry Pi and a USB-to-IDE or USB-to-SATA plus external drive is fine.
* CD/DVD/BluRay disk
* Packages installed: `wodim` (provides `readom` command), `make`, `sed`, `gnuplot`

For example, on a Debian-based OS (including Ubuntu and Raspberry OS), you can install the prerequisites with:

```bash
sudo apt-get update ; sudo apt-get install wodim make sed gnuplot-nox
```

### Get data

* Put a CD in the drive.
* Run command

<pre>
time readom -noerror -nocorr -c2scan dev=/dev/cdrom 2>&1 | tee some_file_name.log
</pre>

* This will produce a `some_file_name.log` file.

### Get graphs

* Run `make` to process the data.
* This will produce `some_file_name.png` and `some_file_name.pdf`.
