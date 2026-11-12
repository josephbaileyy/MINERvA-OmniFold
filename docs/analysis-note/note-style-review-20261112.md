# Note style review queue, 2026-11-12

All commits listed here are **pending Grok review**. Joseph authorized the nineteen prepared edits and further section commits while Grok is paused. These commits do not merge the draft or replace that review. AUD-N4/N5 and the note-role ruling remain with Grok or Joseph.

## Measurement

The measuring script is unchanged, SHA-256 `06570bcc8e8bae9a99d63337ccd6dfdb0740d12bc5294aab310029a00dfee4d3`. The guarded tuple below is **semicolon rate per 1,000 words / comma-so rate per 1,000 words / median paragraph words / p90 paragraph words / percentage of paragraphs over 150 words / words per sentence**. Each row measures the complete named section file, immediately before and after its commit. Every guarded metric is nonincreasing. The same check was also made for the fixed note corpus and its companion corpus with front matter at every prose commit. Word and paragraph totals are denominators, rather than improvement targets.

The note corpus is the 23 prose files included by `main_note.tex`, plus `selection_features.tex` and `scalar_kinematics.tex`. The companion corpus also includes `main_note.tex`. Preamble and values files are excluded. The exact body file list is:

```text
sec_execsummary.tex
sec_intro.tex
sec_experiment.tex
selection_features.tex
sec_method.tex
sec_systematics.tex
sec_validation.tex
sec_results.tex
sec_3d.tex
scalar_kinematics.tex
sec_eavailw.tex
sec_5d.tex
sec_fived16.tex
sec_joint.tex
sec_fps.tex
sec_summary.tex
app_guide.tex
app_statmethods.tex
app_statmethods_nd.tex
app_negweight.tex
app_response_mismatch.tex
app_landscape.tex
app_pet_pointer.tex
app_release.tex
app_codebase.tex
```

The script strips comments, display equations, floats, references, inline mathematics and some commands. It excludes short fragments and certain heading-led blocks. These are measurements of the declared source corpus, not literal counts of every PDF word or an assessment of semantic quality. Paragraph segmentation and mathematical density can affect comparisons.

## Reference papers

The same script was run on the six reference-paper source corpora. The figures guide editing; no fixed numerical target is substituted for the papers. The H1 corpus includes its distributed supplement. The Wiener-SVD corpus includes the driver and its six uncommented prose inputs; author lists, settings, plotting-only inputs and commented drafts were excluded.

| Reference source | Guarded tuple |
|---|---|
| [Andreassen 1911.09107](https://arxiv.org/abs/1911.09107) | 0.0 / 0.7 / 101 / 179 / 32 / 21.5 |
| [Schmitt 1205.6201](https://arxiv.org/abs/1205.6201) | 1.1 / 0.0 / 64 / 137 / 6 / 19.1 |
| [Tang 1705.03568](https://arxiv.org/abs/1705.03568) | 0.2 / 0.3 / 72 / 233 / 21 / 15.8 |
| [Arratia 2109.13243](https://arxiv.org/abs/2109.13243) | 0.7 / 0.3 / 111 / 199 / 25 / 18.8 |
| [Huetsch 2404.18807](https://arxiv.org/abs/2404.18807) | 1.6 / 0.7 / 71 / 135 / 7 / 17.8 |
| [H1 2108.12376](https://arxiv.org/abs/2108.12376) | 3.1 / 0.0 / 87 / 151 / 12 / 20.6 |

The reference corpora have semicolon rates of 0.0–3.1 and comma-so rates of 0.0–0.7 per thousand words; their paragraph lengths and words per sentence span a wider range. This pass splits changes of subject, method, inference or qualification into complete sentences. It preserves numerical statements, mathematical constructions and scope limits. Matching the references is a continuing editorial comparison, not a claim established by a score.

## Nineteen prepared edits

Each prepared edit has its own commit. The eighth also updates the two exact-line registry citations and regenerates their printed index, because splitting the guide moved the unchanged learner description. The rate-fractions draft was shortened to preserve its section's median paragraph length. Both original rate fractions and the exclusion of separate cross sections are retained.

| Commit | Section; change | Before tuple | After tuple |
|---|---|---|---|
| `cc1adc128e9f` | `sec_fps.tex`; acceptance configuration | 0.0 / 0.0 / 82 / 145 / 0 / 14.2 | 0.0 / 0.0 / 82 / 145 / 0 / 14.2 |
| `e20616dbc3df` | `sec_fps.tex`; zero acceptance validation | 0.0 / 0.0 / 82 / 145 / 0 / 14.2 | 0.0 / 0.0 / 82 / 145 / 0 / 14.2 |
| `245a0bc600a6` | `sec_fps.tex`; statistical only containment | 0.0 / 0.0 / 82 / 145 / 0 / 14.2 | 0.0 / 0.0 / 82 / 145 / 0 / 14.2 |
| `1dad77667586` | `sec_fps.tex`; purity central provenance | 0.0 / 0.0 / 82 / 145 / 0 / 14.2 | 0.0 / 0.0 / 82 / 144 / 0 / 13.6 |
| `220fc9d69ca9` | `sec_fps.tex`; envelope scope | 0.0 / 0.0 / 82 / 144 / 0 / 13.6 | 0.0 / 0.0 / 82 / 144 / 0 / 12.7 |
| `989697ef27d8` | `sec_summary.tex`; outlook shares | 7.3 / 0.0 / 138 / 148 / 0 / 13.8 | 4.8 / 0.0 / 138 / 148 / 0 / 13.3 |
| `7aa1ac264dc5` | `app_guide.tex`; appendix records boundary | 22.0 / 0.0 / 162 / 162 / 100 / 13.8 | 22.0 / 0.0 / 112 / 156 / 33 / 13.8 |
| `958f3c2b16ae` | `app_guide.tex`; repository flux boundary | 22.0 / 0.0 / 112 / 156 / 33 / 13.8 | 22.0 / 0.0 / 96 / 112 / 0 / 13.8 |
| `2184f8bf4954` | `app_guide.tex`; repository calls boundary | 22.0 / 0.0 / 96 / 112 / 0 / 13.8 | 22.0 / 0.0 / 50 / 112 / 0 / 13.8 |
| `cd2df7f56248` | `sec_intro.tex`; iterative method family | 7.5 / 1.1 / 103 / 174 / 22 / 15.9 | 6.4 / 1.1 / 103 / 174 / 22 / 15.6 |
| `a9eac69cf427` | `sec_intro.tex`; background practices | 6.4 / 1.1 / 103 / 174 / 22 / 15.6 | 5.3 / 1.1 / 103 / 174 / 22 / 15.4 |
| `c0407a186a92` | `sec_intro.tex`; subtraction prescriptions | 5.3 / 1.1 / 103 / 174 / 22 / 15.4 | 4.3 / 1.1 / 103 / 174 / 22 / 15.1 |
| `118985749f38` | `sec_intro.tex`; split variation methods | 4.3 / 1.1 / 103 / 174 / 22 / 15.1 | 3.2 / 1.1 / 103 / 174 / 22 / 14.9 |
| `a40dc27861d0` | `sec_intro.tex`; neutrino study boundary | 3.2 / 1.1 / 103 / 174 / 22 / 14.9 | 3.2 / 1.1 / 89 / 156 / 10 / 14.9 |
| `3c8c6c208dcf` | `sec_intro.tex`; descriptive benchmark | 3.2 / 1.1 / 89 / 156 / 10 / 14.9 | 2.1 / 1.1 / 89 / 156 / 10 / 14.4 |
| `32110f640303` | `sec_intro.tex`; reporting bin choice | 2.1 / 1.1 / 89 / 156 / 10 / 14.4 | 2.1 / 0.0 / 89 / 155 / 10 / 14.2 |
| `8c2cc73429da` | `sec_intro.tex`; second motivation boundary | 2.1 / 0.0 / 89 / 155 / 10 / 14.2 | 2.1 / 0.0 / 85 / 109 / 0 / 14.2 |
| `40c2443a382d` | `sec_intro.tex`; third motivation boundary | 2.1 / 0.0 / 85 / 109 / 0 / 14.2 | 2.1 / 0.0 / 85 / 109 / 0 / 14.2 |
| `6c83a597b4d9` | `sec_fps.tex`; rate shares | 0.0 / 0.0 / 82 / 144 / 0 / 12.7 | 0.0 / 0.0 / 82 / 144 / 0 / 12.2 |

## Substantive comparison follow-ups

The findings, evidence and disposition of all 38 note–Supplement pairs are recorded once in [note-paper-differences-20261112.md](note-paper-differences-20261112.md). The four clarification commits also pass the section and corpus guards:

| Commit | Section | Before tuple | After tuple |
|---|---|---|---|
| `e381b6cd7d84` | `sec_experiment.tex` | 4.9 / 0.0 / 140 / 143 / 0 / 20.2 | 4.9 / 0.0 / 72 / 143 / 0 / 19.4 |
| `392586448295` | `sec_method.tex` | 7.4 / 3.5 / 137 / 238 / 47 / 17.6 | 7.0 / 3.5 / 131 / 223 / 36 / 17.5 |
| `5a5582f37503` | `sec_fived16.tex` | 10.5 / 3.0 / 119 / 213 / 27 / 26.4 | 10.3 / 3.0 / 118 / 213 / 24 / 26.1 |
| `3d2f0d0dc08c` | `app_negweight.tex` | 7.6 / 1.0 / 88 / 130 / 10 / 17.1 | 7.6 / 1.0 / 87 / 130 / 10 / 17.1 |

## Section style pass

Each section remains a separate commit. The comparison distinguishes sentence jobs instead of replacing one connector with another. Existing absence-claim support is retained; a copy of the existing coverage search comment follows the claim split in the covariance clarification.

| Commit | Section | Before tuple | After tuple |
|---|---|---|---|
| `8122492cd674` | `sec_systematics.tex` | 9.3 / 3.5 / 109 / 198 / 26 / 19.9 | 7.7 / 2.9 / 109 / 198 / 26 / 19.1 |
| `6aec68a65458` | `sec_validation.tex` | 8.4 / 2.1 / 87 / 128 / 4 / 16.8 | 2.1 / 0.4 / 87 / 128 / 4 / 14.7 |
| `9f7e56b022e0` | `sec_results.tex` | 5.4 / 0.0 / 95 / 144 / 0 / 18.2 | 4.0 / 0.0 / 95 / 144 / 0 / 17.8 |
| `74d9e933edcc` | `app_statmethods_nd.tex` | 13.2 / 3.4 / 82 / 148 / 5 / 18.2 | 3.4 / 2.3 / 76 / 142 / 0 / 15.0 |
| `4283dde2dd05` | `sec_3d.tex` | 5.7 / 1.3 / 97 / 192 / 19 / 17.0 | 4.4 / 1.3 / 97 / 192 / 19 / 16.5 |
| `6a5700a00db0` | `sec_5d.tex` | 6.3 / 2.9 / 97 / 185 / 13 / 19.6 | 4.7 / 2.2 / 97 / 185 / 13 / 18.6 |
| `5739199119e9` | `app_statmethods.tex` | 12.6 / 2.3 / 68 / 137 / 7 / 17.6 | 9.9 / 1.9 / 68 / 137 / 7 / 16.7 |

## Corpus checkpoint

| Corpus | Before the nineteen edits | After the section pass |
|---|---|---|
| note | `{'words': 42954, 'paras': 411, 'median': 93, 'p90': 180, 'gt150': 16, 'semi': 9.4, 'so': 2.3, 'wps': 18.9}` | `{'words': 42980, 'paras': 424, 'median': 89, 'p90': 173, 'gt150': 14, 'semi': 7.8, 'so': 1.9, 'wps': 18.2}` |
| full | `{'words': 43386, 'paras': 416, 'median': 93, 'p90': 180, 'gt150': 16, 'semi': 9.4, 'so': 2.2, 'wps': 19.0}` | `{'words': 43412, 'paras': 429, 'median': 88, 'p90': 173, 'gt150': 14, 'semi': 7.7, 'so': 1.9, 'wps': 18.2}` |

## Commit messages

The complete review sequence after `f632ae12159bcbab7b8ac9e98534e69a300694de` is listed below.

`cc1adc128e9f39aaaf4cb5139ec8127db29648de`

```markdown
[note] Acceptance configuration

Review status: pending Grok review.

Checks: 21 passed
```

`e20616dbc3df1a427a09a04503f45d8db6a3f00b`

```markdown
[note] Zero acceptance validation

Review status: pending Grok review.

Checks: 21 passed
```

`245a0bc600a69ef481413db84adc2fc0808f0460`

```markdown
[note] Statistical only containment

Review status: pending Grok review.

Checks: 21 passed
```

`1dad77667586c2feda61dba54e8ff768f025d78f`

```markdown
[note] Purity central provenance

Review status: pending Grok review.

Checks: 21 passed
```

`220fc9d69ca9f4730fdb6718a44d1e1c03f51f72`

```markdown
[note] Envelope scope

Review status: pending Grok review.

Checks: 21 passed
```

`989697ef27d887870ae3899ac539eb426dcea5d7`

```markdown
[note] Outlook shares

Review status: pending Grok review.

Checks: 21 passed
```

`7aa1ac264dc5812a78fd2e36e6e42eab6015a0c5`

```markdown
[note] Appendix records boundary

Review status: pending Grok review.

Checks: 21 passed
```

`958f3c2b16aea2b6c7dfa5430c517649eceb002d`

```markdown
[note] Repository flux boundary

Review status: pending Grok review.

Checks: 24 passed
```

`2184f8bf49543184fb823abf0e0674fde87bb4e4`

```markdown
[note] Repository calls boundary

Review status: pending Grok review.

Checks: 21 passed
```

`cd2df7f56248742f2de0c38d52d4540f74ba2436`

```markdown
[note] Iterative method family

Review status: pending Grok review.

Checks: 21 passed
```

`a9eac69cf42719cb2813f1356690dac0ec5bea05`

```markdown
[note] Background practices

Review status: pending Grok review.

Checks: 21 passed
```

`c0407a186a925d20b9a0edbd1c51eacce2acf676`

```markdown
[note] Subtraction prescriptions

Review status: pending Grok review.

Checks: 21 passed
```

`118985749f38299758742a4ed8bdc1d1d3023007`

```markdown
[note] Split variation methods

Review status: pending Grok review.

Checks: 21 passed
```

`a40dc27861d07696758a06af5b3f82352ed63da1`

```markdown
[note] Neutrino study boundary

Review status: pending Grok review.

Checks: 21 passed
```

`3c8c6c208dcf7cb4d98a771ddf4e54d3da97f1ef`

```markdown
[note] Descriptive benchmark

Review status: pending Grok review.

Checks: 21 passed
```

`32110f640303b1365a4d21ba9a8d2f082adf7808`

```markdown
[note] Reporting bin choice

Review status: pending Grok review.

Checks: 21 passed
```

`8c2cc73429da984d3f3c69970385a5da648cfe77`

```markdown
[note] Second motivation boundary

Review status: pending Grok review.

Checks: 21 passed
```

`40c2443a382d8e695b6be206ba7a48bb9dc9d1b2`

```markdown
[note] Third motivation boundary

Review status: pending Grok review.

Checks: 21 passed
```

`6c83a597b4d95e5c327c7ba71c64d25b81a02ce0`

```markdown
[note] Rate shares

Review status: pending Grok review.

Checks: 21 passed
```

`e381b6cd7d841879ce1a8745782ac52d6aeadc68`

```markdown
[note] Playlist 1a template composition

Review status: pending Grok review.

Checks: 21 passed
```

`3925864482954bbe32f9ea217d29fea5a1e37cf6`

```markdown
[note] Learner selection scope

Review status: pending Grok review.

Checks: 21 passed
```

`5a5582f3750379c04baf5c59f0ca1b751691fc5d`

```markdown
[note] Covariance units and interval assumptions

Review status: pending Grok review.

Checks: 21 passed
```

`3d2f0d0dc08c8d6fdc5dbdecf50b22913ffc09ad`

```markdown
[note] Purity and refinement study scope

Review status: pending Grok review.

Checks: 21 passed
```

`08106324364ee197ea43146d8ade5484dc35d05a`

```markdown
[note] Record the 38 Supplement paragraph differences

Review status: pending Grok review.

Checks: 21 passed
```

`8122492cd6747ca2efe60284f4c0d97d3867d263`

```markdown
[note] Covariance combination prose

Review status: pending Grok review.

Checks: 21 passed
```

`6aec68a654580c72de0d014421a4d1094b5628f6`

```markdown
[note] Validation questions and scope prose

Review status: pending Grok review.

Checks: 21 passed
```

`9f7e56b022e01832d275663f394c7d1e307f12c7`

```markdown
[note] Two dimensional result prose

Review status: pending Grok review.

Checks: 21 passed
```

`74d9e933edcc81ded1aca7d1eb4776865631cba8`

```markdown
[note] Multidimensional statistical methods prose

Review status: pending Grok review.

Checks: 21 passed
```

`4283dde2dd0582872f77930a366e19448952bfad`

```markdown
[note] Three observable definitions and closure prose

Review status: pending Grok review.

Checks: 21 passed
```

`6a5700a00db0d223ddea26189ae01ff19017b758`

```markdown
[note] Five observable diagnostic prose

Review status: pending Grok review.

Checks: 21 passed
```

`5739199119e90915495985ca7bf275491a91fec6`

```markdown
[note] Statistical construction prose

Review status: pending Grok review.

Checks: 21 passed
```

## Reproducing the source metrics

Save the exact script below as `style_metrics.py`. Extract each section's before/after revisions with `git show <commit>^:docs/analysis-note/<file>` and `git show <commit>:docs/analysis-note/<file>`. Run `python3 -I style_metrics.py 'before=<before-file>' 'after=<after-file>'`. For the corpus checks, place only the files listed above in each snapshot folder and pass its `*.tex` glob as a quoted argument. Add the driver only for the companion corpus.

```python
import re,sys,glob,os
def load(paths):
    s=''
    for p in paths:
        try: s+=open(p,errors='ignore').read()+'\n\n'
        except: pass
    return s
def metrics(s):
    s='\n'.join(l for l in s.split('\n') if not l.lstrip().startswith('%'))
    s=re.sub(r'(?<!\\)%.*','',s)
    s=re.sub(r'\\begin\{(table|figure|equation|align|eqnarray|thebibliography|tabular)\*?\}.*?\\end\{\1\*?\}','',s,flags=re.S)
    s=re.sub(r'\$\$.*?\$\$|\\\[.*?\\\]','',s,flags=re.S)
    paras=[p.strip() for p in re.split(r'\n\s*\n',s)]
    def clean(p):
        p=re.sub(r'\\(cite|ref|eqref|label|[a-z]*ref|fvval|nsec|ssec|sfig|stab|napp)\*?\{[^}]*\}','X',p)
        p=re.sub(r'\$[^$]*\$','X',p); p=re.sub(r'\\[a-zA-Z]+\*?(\[[^]]*\])?','',p); p=re.sub(r'[{}~]',' ',p); return p
    P=[clean(p) for p in paras if not re.match(r'\\(section|subsection|title|author|begin|end|maketitle|bibliography|documentclass|usepackage|newcommand|def)',p)]
    P=[p for p in P if len(p.split())>=25 and p.count('.')>=1]
    L=sorted(len(p.split()) for p in P); w=sum(L)
    semi=sum(p.count(';') for p in P); so=sum(len(re.findall(r',\s+so\s',p)) for p in P)
    sent=sum(len(re.findall(r'[.?!]\s+[A-Z]',p))+1 for p in P)
    return dict(words=w,paras=len(P),median=L[len(L)//2],p90=L[int(.9*len(L))],gt150=round(100*sum(x>150 for x in L)/len(L)),semi=round(1000*semi/w,1),so=round(1000*so/w,1),wps=round(w/sent,1))
for name,pat in [(a,b) for a,b in (x.split('=',1) for x in sys.argv[1:])]:
    files=sorted(glob.glob(pat,recursive=True)); print(name.ljust(22),metrics(load(files)))
```

This register is committed with the following message:

```markdown
[note] Record section metrics and pending reviews

Review status: pending Grok review.
```
