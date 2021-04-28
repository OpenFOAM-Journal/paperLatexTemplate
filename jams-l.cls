% \def\filename{jams-l.cls}
% \def\fileversion{2.02}
% \def\filedate{2016/10/18}
%
% \iffalse meta-comment
%
% American Mathematical Society
% Technical Support
% Publications Technical Group
% 201 Charles Street
% Providence, RI 02904
% USA
% tel: (401) 455-4080
%      (800) 321-4267 (USA and Canada only)
% fax: (401) 331-3842
% email: tech-support@ams.org
%
% Copyright 2007, 2016 American Mathematical Society.
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License, either version 1.3c
% of this license or (at your option) any later version.
% The latest version of this license is in
%   http://www.latex-project.org/lppl.txt
% and version 1.3c or later is part of all distributions of LaTeX
% version 2005/12/01 or later.
% 
% This work has the LPPL maintenance status `maintained'.
% 
% The Current Maintainer of this work is the American Mathematical
% Society.
% 
% \fi

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{jams-l}[2016/10/18 v2.02 JAMS article documentclass]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{amsart}}
\ProcessOptions\relax

\LoadClass{amsart}[2009/07/02]

\def\publname{JOURNAL OF THE\newline
  AMERICAN MATHEMATICAL SOCIETY}

\copyrightinfo{\currentyear}%    % copyright year
  {American Mathematical Society}% copyright holder

%  Set abstract at the end of the paper instead of the topmatter section
\def\@maketitle{%
  \normalfont\normalsize
  \let\@makefnmark\relax  \let\@thefnmark\relax
\ifx\@empty\@date\else \@footnotetext{\@setdate}\fi
  \ifx\@empty\@subjclass\else \@footnotetext{\@setsubjclass}\fi
  \ifx\@empty\@keywords\else \@footnotetext{\@setkeywords}\fi
  \ifx\@empty\thankses\else \@footnotetext{%
    \def\par{\let\par\@par}\@setthanks}\fi
  \@mkboth{\@nx\shortauthors}{\@nx\shorttitle}%
\global\topskip42\p@ % 5.5 picas to the base of the first title line
  \@settitle
  \ifx\@empty\authors \else \@setauthors \fi
  \ifx\@empty\@dedicatory
  \else
    \baselineskip18\p@
    \vtop{\centering{\footnotesize\itshape\@dedicatory\@@par}%
      \global\dimen@i\prevdepth}\prevdepth\dimen@i
  \fi
  \normalsize
  \dimen@34\p@ \advance\dimen@-\baselineskip
  \vskip\dimen@\relax
} % end \@maketitle

%  This will set the abstract at the end of the paper before the address
\def\enddoc@text{\@setabstract
  \ifx\@empty\@translators \else\@settranslators\fi
  \ifx\@empty\addresses \else\@setaddresses\fi
}

\def\ISSN{0894-0347}

\endinput
