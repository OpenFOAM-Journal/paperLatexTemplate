% \def\filename{ofj.cls}
% \def\fileversion{1.01}
% \def\filedate{2020/09/23}
%
% \iffalse meta-comment
%
% OpenFOAM Journal
%
% This work is a derivative of the American Mathematical Society
% original file: jams-l.cls
%
% The file was modified to fit the purpose of the OpenFOAM Journal
% at journal.openfoam.com
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
% Copyright 2020 OpenFOAM Journal
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
\ProvidesClass{ofj}[2020/09/23 v1.01 OpenFOAM Journal article documentclass]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ofjart}}
\ProcessOptions\relax

\LoadClass{ofjart}[2020/09/23]

\RequirePackage[margin=2.5cm]{geometry}
\RequirePackage{booktabs}
\RequirePackage[colorlinks=true,linkcolor=black,anchorcolor=black,citecolor=black,filecolor=black,menucolor=black,runcolor=black,urlcolor=black]{hyperref}
\RequirePackage{graphicx}
\RequirePackage{amsmath}
\RequirePackage{algorithmic} %Typesetting complex algorithmic constructs
\def\lstbasicfont{\fontfamily{pcr}\selectfont}
\RequirePackage{listings}\lstset{%
    basicstyle=\small\lstbasicfont,
    keywordstyle=\color{black}\bfseries,
    stringstyle=\ttfamily,
    showstringspaces=false,
    captionpos=b,
    commentstyle=\color{gray},
    frame=single,
    frameround=fttt,
    language=C++,
    numbers=left}

\def\publname{\includegraphics[scale=1.0]{OpenFOAMJournal.pdf}\\[0.15em]}

\copyrightinfo{\currentyear}%    % copyright year
  {OpenFOAM$^{\textregistered}$ Journal}% copyright holder

\newcommand{\@OpenFOAMversions}{}
\newcommand{\OpenFOAMversions}[1]{\renewcommand{\@OpenFOAMversions}{#1}}
\newcommand{\theOpenFOAMversions}{\@OpenFOAMversions}

\newcommand{\@DOI}{}
\newcommand{\DOI}[1]{\renewcommand{\@DOI}{#1}}
\newcommand{\theDOI}{\@DOI}

\newcommand{\@Repository}{}
\newcommand{\Repository}[1]{\renewcommand{\@Repository}{#1}}
\newcommand{\theRepository}{\@Repository}



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
\global\topskip62\p@ % 5.5 picas to the base of the first title line
  \@settitle
  \ifx\@empty\authors \else \@setauthors \fi
    \ifx\@empty\center{\addresses} \else\center{\@setaddresses}\fi
  \ifx\@empty\@dedicatory
  \else
    \baselineskip18\p@
    \vtop{\centering{\footnotesize\itshape\@dedicatory\@@par}%
      \global\dimen@i\prevdepth}\prevdepth\dimen@i
  \fi
  \bigskip

  % Software and Manuscript
  \begin{description}
    \item[DOI] \href{https://doi.org/\theDOI}{\@DOI}\\
    \item[Version(s)] \@OpenFOAMversions\\
    \item[Repo] \href{\theRepository}{\@Repository}
  \end{description}
  \medskip
  \normalsize
  \dimen@34\p@ \advance\dimen@-\baselineskip
  \vskip\dimen@\relax\@setabstract
} % end \@maketitle

%  This will set the abstract at the end of the paper before the address
%\def\enddoc@text{\@setabstract
%  \ifx\@empty\@translators \else\@settranslators\fi
%  \ifx\@empty\addresses \else\@setaddresses\fi
%}

\def\ISSN{xxxx-yyyy}

\endinput
