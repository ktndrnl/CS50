from dateutil import parser


def str_to_datetime(string):
    return parser.parse(string)
