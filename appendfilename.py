#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Time-stamp: <2017-08-22 13:12:11 vk>

## TODO:
## * fix parts marked with «FIXXME»

## ===================================================================== ##
##  You might not want to modify anything below this line if you do not  ##
##  know, what you are doing :-)                                         ##
## ===================================================================== ##

## NOTE: in case of issues, check iCalendar files using: http://icalvalid.cloudapp.net/

import re
import sys
import os
import time
import logging
from optparse import OptionParser
import readline  # for raw_input() reading from stdin

PROG_VERSION_NUMBER = "0.3"
PROG_VERSION_DATE = "2015-04-05"
INVOCATION_TIME = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
FILENAME_TAG_SEPARATOR = ' -- '  # between file name and (optional) list of tags
BETWEEN_TAG_SEPARATOR = ' '  # between tags (not that relevant in this tool)
TEXT_SEPARATOR = ' '  # between old file name and inserted text

USAGE = "\n\
    " + sys.argv[0] + " [<options>] <list of files>\n\
\n\
This tool inserts text between the old file name and optional tags or file extension.\n\
\n\
\n\
Text within file names is placed between the actual file name and\n\
the file extension or (if found) between the actual file namd and\n\
a set of tags separated with \"" + FILENAME_TAG_SEPARATOR + "\".\n\
  Update for the Boss " + TEXT_SEPARATOR + "<NEW TEXT HERE>.pptx\n\
  2013-05-16T15.31.42 Error message" + TEXT_SEPARATOR + "<NEW TEXT HERE>" \
    + FILENAME_TAG_SEPARATOR + "screenshot" + BETWEEN_TAG_SEPARATOR + "projectB.png\n\
\n\
Example usages:\n\
  " + sys.argv[0] + " --text=\"of projectA\" \"the presentation.pptx\"\n\
      ... results in \"the presentation" + TEXT_SEPARATOR + "of projectA.pptx\"\n\
  " + sys.argv[0] + " \"2013-05-09T16.17_img_00042 -- fun.jpeg\"\n\
      ... with interactive input of \"Peter\" results in:\n\
          \"2013-05-09T16.17_img_00042" + TEXT_SEPARATOR + "Peter -- fun.jpeg\"\n\
\n\
\n\
:copyright: (c) 2013 or later by Karl Voit <tools@Karl-Voit.at>\n\
:license: GPL v3 or any later version\n\
:URL: https://github.com/novoid/filetag\n\
:bugreports: via github or <tools@Karl-Voit.at>\n\
:version: " + PROG_VERSION_NUMBER + " from " + PROG_VERSION_DATE + "\n"


## file names containing optional tags matches following regular expression
FILE_WITH_EXTENSION_REGEX = re.compile("(.*?)(( -- .*)?(\.\w+?)?)$")
FILE_WITH_EXTENSION_BASENAME_INDEX = 1
FILE_WITH_EXTENSION_TAGS_AND_EXT_INDEX = 2



## RegEx which defines "what is a file name component" for tab completion:
FILENAME_COMPONENT_REGEX = re.compile("[a-zA-Z]+")

## blacklist of lowercase strings that are being ignored for tab completion
FILENAME_COMPONENT_LOWERCASE_BLACKLIST = ['img', 'eine', 'einem', 'eines', 'fuer', 'haben',
                                          'machen', 'macht', 'mein', 'meine', 'meinem',
                                          'meinen', 'meines', 'neuem', 'neuer', 'neuen', 'vkvlc']

## initial CV with strings that are provided for tab completion in any case (whitelist)
INITIAL_CONTROLLED_VOCABULARY = ['Karl', 'Graz', 'LaTeX', 'specialL', 'specialP']

parser = OptionParser(usage=USAGE)

parser.add_option("-t", "--text", dest="text",
                  help="the text to add to the file name")

parser.add_option("-s", "--dryrun", dest="dryrun", action="store_true",
                  help="enable dryrun mode: just simulate what would happen, do not modify file(s)")

parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  help="enable verbose mode")

parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
                  help="enable quiet mode")

parser.add_option("--version", dest="version", action="store_true",
                  help="display version and exit")

(options, args) = parser.parse_args()


def handle_logging():
    """Log handling and configuration"""

    if options.verbose:
        FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    elif options.quiet:
        FORMAT = "%(levelname)-8s %(message)s"
        logging.basicConfig(level=logging.ERROR, format=FORMAT)
    else:
        FORMAT = "%(levelname)-8s %(message)s"
        logging.basicConfig(level=logging.INFO, format=FORMAT)


def error_exit(errorcode, text):
    """exits with return value of errorcode and prints to stderr"""

    sys.stdout.flush()
    logging.error(text)
    input('Press <Enter> to finish with return value %i ...' % errorcode).strip()
    sys.exit(errorcode)


class SimpleCompleter(object):
    ## happily stolen from http://pymotw.com/2/readline/

    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s
                                for s in self.options
                                if s and s.startswith(text)]
                logging.debug('%s matches: %s', repr(text), self.matches)
            else:
                self.matches = self.options[:]
                logging.debug('(empty input) matches: %s', self.matches)

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        logging.debug('complete(%s, %s) => %s',
                      repr(text), state, repr(response))
        return response


def locate_and_parse_controlled_vocabulary():
    """This method is looking for filenames in the current directory
    and parses them. This results in a list of words which are used for tab completion.

    @param return: either False or a list of found words (strings)

    """

    cv = INITIAL_CONTROLLED_VOCABULARY
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        ## extract all words from the file name that don't contain numbers
        new_items = FILENAME_COMPONENT_REGEX.findall(os.path.splitext(os.path.basename(f))[0])
        ## remove words that are too small
        new_items = [item for item in new_items if len(item) > 3]
        ## remove words that are listed in the blacklist
        new_items = [item for item in new_items if item.lower() not in FILENAME_COMPONENT_LOWERCASE_BLACKLIST]
        ## remove words that are already in the controlled vocabulary
        new_items = [item for item in new_items if item not in cv]
        ## append newly found words to the controlled vocabulary
        cv.extend(new_items)

    if len(cv) > 0:
        return cv
    else:
        return False


def handle_file(filename, text, dryrun):
    """
    @param filename: one file name
    @param text: string that shall be added to file name(s)
    @param dryrun: boolean which defines if files should be changed (False) or not (True)
    @param return: error value
    """

    assert(isinstance(filename, str))

    if os.path.isdir(filename):
        logging.warning("Skipping directory \"%s\" because this tool only processes file names." % filename)
        return
    elif not os.path.isfile(filename):
        logging.error("Skipping \"%s\" because this tool only processes existing file names." % filename)
        return

    components = re.match(FILE_WITH_EXTENSION_REGEX, os.path.basename(filename))
    if components:
        old_basename = components.group(FILE_WITH_EXTENSION_BASENAME_INDEX)
        tags_with_extension = components.group(FILE_WITH_EXTENSION_TAGS_AND_EXT_INDEX)
    else:
        logging.error('Could not extract file name components of \"%s\". Please do report.' % str(filename))
        return

    try:
        new_filename = os.path.join(os.path.dirname(filename), old_basename + TEXT_SEPARATOR + text + tags_with_extension)
    except:
        error_exit(7, "Error while trying to build new filename: " + str(sys.exc_info()[0]))
    assert(isinstance(new_filename, str))

    if dryrun:
        logging.info(" ")
        logging.info(" renaming \"%s\"" % filename)
        logging.info("      ⤷   \"%s\"" % (new_filename))
    else:
        logging.debug(" renaming \"%s\"" % filename)
        logging.debug("      ⤷   \"%s\"" % (new_filename))
        try:
            os.rename(filename, new_filename)
        except:
            error_exit(9, "Error while trying to rename file: " + str(sys.exc_info()))


def main():
    """Main function"""

    if options.version:
        print(os.path.basename(sys.argv[0]) + " version " + PROG_VERSION_NUMBER + \
            " from " + PROG_VERSION_DATE)
        sys.exit(0)

    handle_logging()

    if options.verbose and options.quiet:
        error_exit(1, "Options \"--verbose\" and \"--quiet\" found. " +
                   "This does not make any sense, you silly fool :-)")

    text = options.text

    if not text:

        logging.debug("interactive mode: asking for text ...")
        logging.info("Add text to file name ...")

        vocabulary = locate_and_parse_controlled_vocabulary()
        if vocabulary:

            assert(vocabulary.__class__ == list)

            # Register our completer function
            readline.set_completer(SimpleCompleter(vocabulary).complete)

            # Use the tab key for completion
            readline.parse_and_bind('tab: complete')

            tabcompletiondescription = '; complete ' + str(len(vocabulary)) + ' words with TAB'

        print('         (abort with Ctrl-C' + tabcompletiondescription + ')')
        print()
        text = input('Please enter text: ').strip()

        if not text or len(text) < 1:
            logging.info("no text given, exiting.")
            sys.stdout.flush()
            sys.exit(0)

        logging.info("adding text \"%s\" ..." % text)

    logging.debug("text found: [%s]" % text)

    logging.debug("extracting list of files ...")
    logging.debug("len(args) [%s]" % str(len(args)))
    if len(args) < 1:
        error_exit(2, "Please add at least one file name as argument")
    files = args
    logging.debug("%s filenames found: [%s]" % (str(len(files)), '], ['.join(files)))

    logging.debug("iterate over files ...")
    for filename in files:
        handle_file(filename, text, options.dryrun)

    logging.debug("successfully finished.")
    if options.verbose:
        input('Please press <Enter> for finishing...').strip()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:

        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################

#end
