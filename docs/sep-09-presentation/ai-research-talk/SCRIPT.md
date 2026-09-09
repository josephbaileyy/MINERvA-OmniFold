# Research with AI as an undergraduate — Joseph Bailey

Working spoken draft: 16 main slides and seven optional backup slides. Personal reflections use Joseph's supplied account; suggested next steps are proposals. Pause on the physics plots rather than reading every number. References, definitions and qualifications are in EVIDENCE.md.

## 01 — Research with AI as an undergraduate

Hello everyone! I'm Joseph, a physics undergraduate and CS coterm, entering my fourth year. I've met some of you informally, and I'd love to hear more about your research and graduate-school experiences afterward, because I'm starting to apply to PhD programs.

Today I'll introduce the MINERvA unfolding project I've been working on, and use it to ask a question about doing research with AI: how much did my particular approach help me produce useful research, and what did it do to my experience as a student?

Those are different questions. I can show you research outputs and concrete failures we caught. I'm less confident that I can tell you how much time I saved, or how much of the implementation I could explain without help. That uncertainty is part of what I want to discuss.

## 02 — The starting point: an open analysis + OmniFold

I started this project last December. Ben mentioned how OmniFold worked, and I nodded because I thought I understood. I really didn't.

He also pointed me toward MINERvA, a neutrino–nucleus experiment using the NuMI beam at Fermilab, which had released public material for this analysis. Applying OmniFold looked like a natural extension. I gave the public tutorial and Ryan Milton's unbinned-unfolding repository to several LLMs and asked them to help put the pieces together.

At a high level, unfolding tries to infer a distribution before detector effects from what we observe after those effects. OmniFold uses classifiers to learn weights that make simulated reconstructed events resemble the data. Information from those weights is transferred back to the simulated truth distribution through an iterative procedure. This diagram leaves out the practical details, including acceptance and background treatment.

My first target was the published inclusive cross section in two components of muon momentum: transverse momentum and momentum along the beam. That gave me something unusually useful for an AI-assisted project: an existing result against which I could check the output.

## 03 — How closely does the 2D result reproduce the paper?

Here are the two projections of the frozen two-dimensional result. Teal is my OmniFold result with its total uncertainty band; the black points are the published cross section with the paper's total uncertainties. The lower panels show the ratio of the central values. Teal error bars divide my uncertainty by the paper's central value, while the gray band shows the paper's relative uncertainty around one.

The shapes are close over the reported range. The integrated cross sections are about 3.073 and 3.039 times ten to the minus 38 square centimeters per nucleon, so they differ by about 1.1 percent. I reproduced the two-dimensional result early enough to present it to the MINERvA collaboration. These plots use the later frozen result documented in the repository, rather than claiming this exact file was the early presentation result.

There is a small but real metadata qualification: three transverse-momentum boundaries differ by 0.005 GeV/c between the frozen files. Each projection uses its own actual bin widths, and the ratio compares corresponding bins. I have not silently rebinned or modified either result.

My band includes systematic, bootstrap-statistical and ML uncertainty. For each projection I propagate the full covariance, including correlations between bins. Both results have uncertainties, but neither the overlapping bands nor the ratio bars give an uncertainty on their difference: these results use shared data and systematic inputs. Agreement with the paper is useful evidence, alongside the completed closure, completeness and iteration controls; it is not an independent-measurement significance test.

## 04 — The full 2D comparison shows where differences live

Projections can hide compensating differences. This is every reported two-dimensional bin, showing the percentage difference between my central value and the paper's corresponding central value. Gray cells are outside the reported mask. The axes give physical bin ranges, but each cell has the same display width so you can inspect the whole grid.

Of the 205 reported bins, 159 are within five percent, and 193 are within ten percent. Three differ by more than twenty percent. The color scale saturates at plus or minus twenty percent, so the larger differences are printed explicitly instead of disappearing into the color scale.

This is the kind of plot I would want to see before accepting a broad statement that a reproduction worked. It shows both the substantial agreement and the exceptions. The three slightly different transverse-momentum boundaries still apply to this corresponding-bin comparison; the row labels use my file's boundaries.

I would describe this as close reproduction across most reported bins, supported by the separate validation controls. I would not call every colored residual a significant discrepancy, or assume the residual map alone establishes correctness.

## 05 — The agreement survives looking inside the projections

These are four slices through the two-dimensional distribution, spanning low to high transverse momentum. Within each slice, the horizontal axis is longitudinal momentum on a log scale. The teal curve and shaded band are my result and its total uncertainty. The black points and gray ratio band use the paper's central values and total uncertainties. The teal ratio bars are my uncertainty divided by the paper central value, with that denominator held fixed. These are separately displayed errors, not an uncertainty on the difference.

The slices were selected to span the transverse-momentum range while having exactly the same physical boundaries in both files. They weren't selected by which ratios looked best. All fourteen slices, including those with different boundaries, are in the backup slides.

This view is useful because you can see the cross-section shape and the relative difference together. A ratio alone can make a low-rate tail look just as consequential as the peak; a cross-section plot alone can conceal a relative difference in that tail. The powers of ten differ between panels because the rates differ substantially.

For this project, the two-dimensional case gave me an external target before moving into a setting where there was no published higher-dimensional answer to reproduce.

## 06 — Flux and muon reconstruction dominate our errors

The error bars are more useful if we can explain what sets their size. This plot breaks our two-dimensional uncertainty into sources and compares the available published components. For each component, I project its full covariance into transverse or longitudinal momentum and then summarize the relative errors by their median across the projected bins.

Flux is the largest contribution: about 4.9 percent in our projections, compared with about 4.0 percent from the paper's released flux covariance. Muon reconstruction is the next largest contribution in ours, followed by the target-normalization uncertainty. Statistical and unfolding-model seed variation are smaller here. ML on this plot means stochastic variation of the unfolding model, not uncertainty about the LLMs helping me do the work.

The black markers appear only where the paper released a corresponding component. A missing marker does not mean the paper has zero error from that source. It released a muon-energy-scale covariance, which is narrower than our full muon-reconstruction group; the direct energy-scale comparison is in backup.

These are not stacked shares of a budget. Covariances are combined before projection, and medians of relative standard deviations do not add. Also, similar median errors over the original two-dimensional bins do not require identical projected errors: the correlations matter.

## 07 — The scope expanded beyond the published reference

From there I extended the analysis to available energy in three dimensions, and to scalar four- and five-dimensional descriptions including q3 and W. The central values and closure checks are validated, but their uncertainty construction is a separate, unresolved part of the work. The higher-dimensional covariance products are not adopted publication results.

That distinction matters. Recovering the two-dimensional marginal is a useful anchor. Injecting a shape and checking whether the method recovers it is another useful test. Neither automatically validates a complete covariance or every possible source of bias.

I've also explored full-event representations, informed by Gregor's work and the OmniLearn/PET work associated with Vinicius Mikuni and Ben. That part is diagnostic and method development, not a publication uncertainty product.

As the project expanded, the task for the models changed. Early on, I could ask whether the result resembled a published answer. Later I needed help deciding what evidence would establish that an unfamiliar analysis step worked. That increased both the potential value of assistance and the difficulty of judging it.

## 08 — Beyond reproduction: a feature the generators miss

The higher-dimensional analysis also gives us a physics question. In the region with available energy at least 0.8 GeV and W at least 1.8 GeV, the unfolded central value is larger than the prediction from each of these four generator configurations.

These points compare cross sections integrated over the same nine cells. Data divided by generator ranges from about 1.54 to 1.61. The dashed line at one means equal central values. Adding Valencia MEC to GENIE does not close this particular gap: the ratio moves from 1.535 to 1.579. That is an observation about these predictions, not a determination of the missing physical mechanism.

There are deliberately no uncertainty bars here because the covariance needed to assess the significance of this higher-dimensional comparison is not adopted. The precise claim is that these central predictions miss this feature of the unfolded result.

This is the scientific payoff behind increasing the scope. Reproducing an existing measurement established a reference point; the extension lets us ask where models describe the data differently. It also makes clear why producing more analysis code and finishing the research are not the same milestone.

## 09 — The workflow became a project of its own

The earliest approach was straightforward: give several models the tutorial and existing software, ask questions, and try to get the reproduction working.

By mid-July, the records describe a coordinator assigning bounded tasks to workers, with separate verification and review roles. That was an attempt to make larger investigations manageable and avoid having every agent improvise the entire project.

The next layer was keeping the work moving between model turns. July records describe scripts detecting events and waking an agent, and August records include an explicit campaign queue. Those are documented milestones, not clean experimental periods: the approaches overlapped and kept changing.

The attractive idea was that a model could do useful reasoning while ordinary tools handled scheduling and state. But building that separation required work of its own. The machinery for coordinating research became a substantial engineering problem, and it competed with learning and thinking about the physics.

## 10 — Activity grew. Was the work more effective?

The repository became much more active: 263 non-merge commits in July and 1,970 in August. The right-hand plot asks where edits occurred. The orchestration directories accounted for about 27 percent of commit-and-path touches in July and 63 percent in August.

A touch means that one path appears in one commit. These are not hours. A large commit and a small commit each count once on the left; the directory categories also mix purposes. Orchestration directories contain scientific receipts, and analysis directories contain process code.

What the plot establishes is growth in recorded activity and a shift in its location. My recollection supplies another piece: much of my active time went into debugging orchestration and routing. Those observations fit together, but the percentages on the plot are not a measurement of my time allocation.

To answer whether progress sped up, I would want time to an accepted research result, including my intervention time and later rework. This history doesn't provide a matched baseline for that. More activity could represent more output, more overhead, or both.

## 11 — A saved model did not reproduce the event weights

A checkpoint is a saved snapshot of the unfolding neural network's learned parameters: the numerical coefficients that determine its predictions. It lets us load that fitted network again without retraining it. This is a checkpoint of the physics-analysis model, not of an LLM conversation.

An epoch is a pass through the training data. The last epoch is the state reached when training finishes. The best validation epoch is the state with the lowest loss on held-out validation data, and it can occur earlier. Best here means best according to that training criterion, not proven best for the physics result.

In this historical diagnostic run, the analysis generated event weights using the last-epoch network still in memory, while the checkpoint file saved the best-validation network. Loading the file therefore loaded a different set of learned parameters from those used by the original run.

There are two different kinds of weights here. The neural network's learned parameters determine its outputs. Those outputs are used to calculate a weight for each simulated event, and those event weights determine the unfolded distribution. The bars show differences in the event weights, not differences in network parameters.

The aggregate ratio differed by less than 0.0001, but individual event weights could differ substantially: the median relative difference was about 0.8 percent, the ninetieth percentile about 17 percent, and the maximum 86.6 percent. That maximum does not mean the total cross section changed by 86.6 percent.

A corrected rerun made the stored and reloaded event weights agree exactly at the matched batch size. I am not claiming I independently discovered the defect. The lesson from the recorded example is that reproducing a result requires the saved model to be the model that actually produced its event weights. A similar aggregate number did not establish that identity.

## 12 — The friction: auditing before trying anything

My biggest frustration is that AI often takes a long time because it wants to audit everything before doing anything. I often want to try a small experiment, see what happens, and then use the result to decide where to look.

The checkpoint example is a reason to keep meaningful checks. It isn't a reason to make every cheap exploratory question wait for a broad review of the project. What I want to improve is the order: identify the uncertainty, choose a bounded experiment that can resolve it, and inspect the evidence it produces.

For a cheap and reversible test, trying something can be the fastest way to learn. Before an expensive production run or accepting a scientific claim, the relevant evidence and provenance checks still matter. The right sequence depends on the decision and its cost.

This is my experience and a proposed adjustment to my method. I haven't measured how much time it would save. A useful comparison would track time to first plausible output, time to accepted output, my active minutes, and how often the result needed substantive correction.

## 13 — My active time shifted into orchestration and routing

When I think about where my own active minutes went, I remember debugging the LLM orchestration and routing issues. The historical logs contain very concrete examples: a wakeup targeting an executable path that didn't exist, and a Python environment mismatch preventing the watcher from running correctly.

Those failures are separate from whether a model could reason about unfolding. An excellent answer doesn't help if the right process never starts, or if the work is routed to the wrong environment.

One question I asked was, “Why do we even need an LLM for the watcher?” If the task is to report a defined job outcome, an ordinary script can often express that rule directly. The record includes a replacement implementation and tests; I am not claiming a measured deployment-wide saving from that change.

This is why I want to evaluate the whole method, not just the model's best answer. The cost includes coordinating the agents, recovering from tool failures, reviewing outputs and keeping the pieces consistent. In my experience, that coordination cost was prominent enough to be part of the research story.

## 14 — Outside expertise corrected the question itself

Here is a concrete example of why outside expertise mattered. A question in the project records was framed around there being no prior MINERvA three-dimensional unfolding result. The clarification recorded in August was that MINERvA already had such a publication, and we had found and cited it.

The mistake was in how the question was framed. The distinction needed to be the unbinned, simultaneous formulation, rather than simply reaching three dimensions. The record also says the separate question about endorsing a covariance publication remained unanswered. A useful conversation was not the same thing as endorsement.

I am not claiming this proves AI caused the mistake, or that I independently found it. What it shows is that checking the output of a pipeline does not check every premise around the research. Literature context and expert conversation answer questions that a numerical reproduction cannot.

For me as an undergraduate, this is a useful complement to asking models for explanations. I need to be able to state what is new, why it matters, and which parts of that account have actually been checked. That connects directly to my uncertainty about how much I understand without assistance.

## 15 — I have a high-level map. Do I understand the details?

My honest answer is that I don't know how much I could explain without AI. It abstracts so much away that I feel I mainly have high-level ideas of how things work.

There might be a benefit to that abstraction. Maybe it lets me move between approaches without becoming too attached to one implementation or getting stuck in a rabbit hole. But that is a hypothesis about my experience, not evidence that I learned more or made better decisions.

The other possibility is that I can operate a pipeline while missing a detail that would change how I interpret its output. A successful reproduction helps test the pipeline. It doesn't automatically test my understanding of why it works.

One concrete practice I would like to add is to make a prediction before asking the model: if I change the binning, normalization or an input distribution, what should happen, and why? Then compare that prediction with the result and explain the evidence without leaning on the model's summary. That would give me something more tangible to assess than how familiar an explanation feels while I'm reading it.

## 16 — Real research output; an unresolved net benefit

My assessment is mixed. The project produced a two-dimensional reproduction with completed controls and higher-dimensional central results with closure checks. AI assistance was part of how I got there. That is a concrete outcome, even though I don't have the no-AI version of this project to compare against.

I would keep the ability to ask basic questions freely, get help implementing unfamiliar work, and test outputs against external references and closure studies. I would change how much machinery I build around that assistance, make exploratory tasks smaller, and record my own intervention time.

For my development as a researcher, I also want to practice explaining the decisions that determine the scientific result. A larger project isn't automatically a better educational experience if I can't defend its essential steps.

So I wouldn't call the whole effort a waste, and I can't claim a measured net speedup. The useful question is which kinds of delegation produce accepted results at a reasonable total cost while leaving me able to understand and defend them. If you were supervising this project, what would you ask a student to demonstrate before delegating this much?

## 17 — Backup: all 14 transverse-momentum slices

This is the complete slice inventory. Every transverse-momentum row is shown, with the same reported-bin mask as the main comparison. Panels whose transverse-momentum boundaries differ between files explicitly print the paper's range as well.

The longitudinal-momentum axis is logarithmic, and the density scale changes between panels. The teal bands use my total covariance diagonal for individual bins, and the teal ratio bars divide those errors by the paper central value. Black errors and gray ratio bands come from the paper's total covariance diagonal. They display each result's errors separately, not an uncertainty on the difference. The accompanying vector PDF can be enlarged to inspect these small panels.

## 18 — Backup: cumulative agreement counts

The agreement windows are cumulative. Of 205 reported bins, 159 are within five percent, 193 within ten percent, and 202 within twenty percent of the corresponding published central value. These are approximately 77.6, 94.1 and 98.5 percent of the reported bins.

The totals integrate each file using its actual bin areas. The small transverse-momentum boundary differences are recorded in the comparison metadata. These descriptive counts are not confidence levels, and the total agreement should be read alongside the residual map and completed validation controls.

## 19 — Backup: normalization can hide behind a reassuring ratio

The differential bin contents need to be multiplied by bin areas before summing to obtain a total cross section. If I simply sum the densities, I get a different quantity with different units.

Here the properly integrated ratio is about 1.0113, while the ratio of bare sums is about 1.0115. Both ratios look reassuringly close to one. Only the first row is a total cross section.

This is a useful question to be able to answer myself: what quantity am I comparing, and what operation gives it the stated units? Agreement between two numbers cannot supply a missing definition.

## 20 — Backup: repository size and complexity

This plot counts tracked Python files at fixed monthly snapshots. It includes tests, drivers and vendored files, so it measures the stock of code paths, not the size of the essential method or my understanding of it.

We considered an entropy metric. Entropy over file-edit frequencies would describe how concentrated edits were across files. It would not directly measure code complexity, scientific progress, maintainability or student learning. I don't want to introduce an impressive-sounding metric whose interpretation is weaker than the simple observations already available.

## 21 — Backup: what this case study can establish

The available evidence includes research components with documented controls, historical failure-and-repair examples, descriptive repository measurements, and my own account of the experience.

What is missing is a matched no-AI baseline, reliable human-hours accounting, a controlled comparison of models, and a learning assessment. Models, project scope and orchestration changed together.

A future comparison could assign comparable bounded tasks to different workflows with the same acceptance criteria, then record time to accepted output, human intervention, substantive rework and what I could explain afterward. That is a proposal for stronger evidence, not a result of this retrospective.

## 22 — Backup: comparing the sources released with the paper

The public ROOT file provides separate total, flux, statistical and muon-energy-scale covariances. Here those are compared with the corresponding sources in our two-dimensional construction, using each result's own physical bin widths and projected central value.

Our energy-scale category is the sum of the MINOS and MINERvA muon-energy bands. It excludes the efficiency, resolution and beam-angle terms that were included in the broader reconstruction group on the main slide. These are comparable source labels, not a claim that every underlying nuisance prescription or correlation is identical.

The bars and markers are medians across projected bins. The full arrays are exported with the presentation so the medians do not conceal the definition of the calculation. This comparison explains the broad budget; it does not establish statistical compatibility between the two unfolded results.

## 23 — Backup: references and scientific scope

These are the research and software sources behind the project: the MINERvA inclusive measurement, OmniFold, the unbinned-unfolding tools, OmniLearn/PET, and the MINERvA foundation-model work that informed the full-event direction.

The accompanying evidence file records the receipt paths, frozen source revision, input hashes and figure calculations. The two-dimensional result is complete on central value and uncertainty. Higher-dimensional central values have validation controls, while their covariance adoption remains unresolved. The full-event PET work shown here is diagnostic and method development.
