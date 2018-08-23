# Copyright 2018 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Module containing methods needed to load skill
data such as dialogs, intents and regular expressions.
"""

from os import listdir
from os.path import splitext, join
import re

from mycroft.messagebus.message import Message
from mycroft.util.parse import normalize


def load_vocab_from_file(path):
    """Load Mycroft vocabulary from file
    The vocab is sent to the intent handler using the message bus

    Args:
        path:           path to vocabulary file (*.voc)
    """
    if path.endswith('.voc'):
        with open(path, 'r') as voc_file:
            for line in voc_file.readlines():
                if line.startswith("#"):
                    continue
                yield line.strip()


def load_regex_from_file(path):
    """Load regex from file
    The regex is sent to the intent handler using the message bus

    Args:
        path:       path to vocabulary file (*.voc)
        bus:        Mycroft messagebus connection
    """
    if path.endswith('.rx'):
        with open(path, 'r') as reg_file:
            for line in reg_file.readlines():
                if line.startswith("#"):
                    continue
                re.compile(line.strip())
                yield line.strip()


def load_vocabulary(basedir, bus, skill_id, lang='en-us'):
    """Load vocabulary from all files in the specified directory.

    Args:
        basedir (str): path of directory to load from
        bus (messagebus emitter): messagebus instance used to send the vocab to
                                  the intent service
        skill_id: skill the data belongs to
    """
    for vocab_file in listdir(basedir):
        if vocab_file.endswith(".voc"):
            vocab_type = to_alnum(skill_id) + splitext(vocab_file)[0]
            voc_path = join(basedir, vocab_file)
            for line in load_vocab_from_file(voc_path):
                parts = normalize(line.strip(), lang=lang).split("|")
                entity = parts[0]
                bus.emit(Message("register_vocab", {
                    'start': entity, 'end': vocab_type
                }))
                for alias in parts[1:]:
                    bus.emit(Message("register_vocab", {
                        'start': alias, 'end': vocab_type, 'alias_of': entity
                    }))


def load_regex(basedir, bus, skill_id, lang='en-us'):
    """Load regex from all files in the specified directory.

    Args:
        basedir (str): path of directory to load from
        bus (messagebus emitter): messagebus instance used to send the vocab to
                                  the intent service
        skill_id (str): skill identifier
        lang:           language
    """
    for regex_type in listdir(basedir):
        if regex_type.endswith(".rx"):
            rx_path = join(basedir, regex_type)
            for line in load_regex_from_file(rx_path):
                line = normalize(line, lang)
                bus.emit(Message("register_vocab",
                                 {'regex': munge_regex(line.strip(),
                                                       skill_id)}))


def to_alnum(skill_id):
    """Convert a skill id to only alphanumeric characters

     Non alpha-numeric characters are converted to "_"

    Args:
        skill_id (str): identifier to be converted
    Returns:
        (str) String of letters
    """
    return ''.join(c if c.isalnum() else '_' for c in str(skill_id))


def munge_regex(regex, skill_id):
    """Insert skill id as letters into match groups.

    Args:
        regex (str): regex string
        skill_id (str): skill identifier
    Returns:
        (str) munged regex
    """
    base = '(?P<' + to_alnum(skill_id)
    return base.join(regex.split('(?P<'))


def munge_intent_parser(intent_parser, name, skill_id):
    """Rename intent keywords to make them skill exclusive
    This gives the intent parser an exclusive name in the
    format <skill_id>:<name>.  The keywords are given unique
    names in the format <Skill id as letters><Intent name>.

    The function will not munge instances that's already been
    munged

    Args:
        intent_parser: (IntentParser) object to update
        name: (str) Skill name
        skill_id: (int) skill identifier
    """
    # Munge parser name
    if str(skill_id) + ':' not in name:
        intent_parser.name = str(skill_id) + ':' + name
    else:
        intent_parser.name = name

    # Munge keywords
    skill_id = to_alnum(skill_id)
    # Munge required keyword
    reqs = []
    for i in intent_parser.requires:
        if skill_id not in i[0]:
            kw = (skill_id + i[0], skill_id + i[0])
            reqs.append(kw)
        else:
            reqs.append(i)
    intent_parser.requires = reqs

    # Munge optional keywords
    opts = []
    for i in intent_parser.optional:
        if skill_id not in i[0]:
            kw = (skill_id + i[0], skill_id + i[0])
            opts.append(kw)
        else:
            opts.append(i)
    intent_parser.optional = opts

    # Munge at_least_one keywords
    at_least_one = []
    for i in intent_parser.at_least_one:
        element = [skill_id + e.replace(skill_id, '') for e in i]
        at_least_one.append(tuple(element))
    intent_parser.at_least_one = at_least_one
