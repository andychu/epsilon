
/*!re2c
re2c:yyfill:enable = 0;
re2c:define:YYCTYPE = char;
re2c:define:YYCURSOR = p;

identifier = "a" . "b" [^c] "d";

identifier { return true; }

*/
