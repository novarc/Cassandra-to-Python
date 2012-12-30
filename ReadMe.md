Cassandra to Python Translator
==============================

Background
----------

I began working on this project as an undergraduate in the *[CSE 487: Research in Computer Science](http://www.cs.sunysb.edu/undergrad/cse_courses/cse487.html)* class at the [Department of Computer Science](http://www.cs.sunysb.edu) in [Stony Brook Univeristy](http://www.stonybrook.edu/). I was advised by [Y. Annie Liu](http://www.cs.sunysb.edu/~liu/), a Professor of Computer Science at Stony Brook University. The need for this translator arose from research she had been conducting in the field of *role-based access control systems* (RBACs). She discovered during her research that although there were many papers and theses written on this topic, most of them lacked sufficiently large test cases based on real-world needs. The exception to this norm that stood out to her was the [PhD. dissertation](http://www.cs.sunysb.edu/~stoller/cse592/becker05cassandra-thesis.pdf) of [Moritz Y. Becker](http://research.microsoft.com/en-us/people/moritzb/). In his dissertation titled *“Cassandra: flexible trust management and its application to electronic health records”*, Becker not only describes a powerful new RBAC-system, but also provides a rich test case drawn from real world needs.

At the center of his thesis, is the goal of providing a desirable security system for the U.K.’s newly proposed Electronic Health Record (EHR) system. The National Health Service (NHS) of the U.K., which is the overseeing body that provides universal health care to all the residents in the United Kingdom, had launched a new project known as the National Programme for Information Technology (NPfIT) – the goal of which, was to centralize and electronically store patient information and provide a secure and reliable way for physicians and others to access them on a need-basis with patient consent. Becker describes the challenging nature of his task at the start of his thesis:

> “What is it that makes access control in this context so very challenging? Firstly, the authorization policies (i.e., the rules governing who can access which resources) can be extremely complex, may partially rely on and interact with policies of other users on the network, and they can frequently change. Secondly, unlike before, access control cannot be solely based on identification and authentication of individuals anymore. In the new environments, subjects wish to collaborate and share their resources with previously unknown users. We therefore need a way to establish trust between mutual strangers.”

He presents as a solution to this, the role-based access control system *Cassandra*. In addition to this, he also provides a complete implementation of an electronic health record system by precisely following NHS’s specification. It is written in a domain specific language (DSL) also called *Cassandra*, which Becker designed explicitly for his RBAC system. The EHR implementation runs over 2000 lines and consists of 375 “policy rules” written in the DSL Cassandra. The primary benefit of this implementation was its large size and the fact that it is based on real-world needs and followed real-world requirements (the NHS’ specification.) As such his implementation of the NHS EHR in Cassandra served as the perfect test case Annie Liu needed to progress her research in RBACs.

However Annie Liu primarily works with the programming language Python and has much invested in it. At the same time she also saw the need to re-organize the Cassandra EHR into an object-oriented model. So when I approached her one summer seeking research projects to work on, she suggested I translate Moritz Becker’s EHR implementation from Cassandra to Python. As I began translating it, I realized the process was slow, tedious and repetitive. I also realized that if I ever wanted to make some stylistic or structural change to the translation it would be nearly impossible as it would require going through the translation and editing it rule-by-rule. To make things more interesting and to add better control over the translation, I asked Annie if I could write a program that automatically translated Cassandra to Python rather than by translating it by hand. She gladly agreed to my suggestion and this project was born.

Overview
--------

The primary building block of the Cassandra role-based access control system are roles. Cassandra regulates and determines who has access to what resources and what information. Cassandra enables the user to lay out the circumstances and necessary credentials required for such access in a Prolog-like language also called *Cassandra*. This language is a derivative of a subset of [Prolog](https://en.wikipedia.org/wiki/Prolog) known as [Datalog](https://en.wikipedia.org/wiki/Datalog). The *Cassandra* language adds to Datalog a feature known as *constraints* (to be explained later), which allows for limited computation within the access control rule set.

In the Cassandra implementation of the NHS EHR, there are many kinds of users - doctors, patients, administrators to name a few. Each of these types of users is represented by a Cassandra *role* in Becker’s implementation of the EHR. In the NHS EHR, there are four separate modules (or sets of rules) that determine the actions that can be taken by user, roles that can be activated by (i.e. applied to) a user and credentials that can be requested (for verification whether a particular user is authorized to perform an action, e.t.c.) Each module is wrapped around by a Cassandra entity which executes the above mentioned queries by evaluating a set of rules and facts unique to that module known as the *Policy*. All four modules operate independently but certain requests, such as a requests for credentials can cross modules. Becker’s Cassandra system is capable of handling such requests regardless of where each entity is located; requests for credentials can be sent over the network to an entity running on a computer in a different city. The four modules that make up the Cassandra EHR are called [Spine](https://github.com/arjungmenon/Cassandra-to-Python/blob/master/ehr/spine.txt), Patient Demographics Service ([PDS](https://github.com/arjungmenon/Cassandra-to-Python/blob/master/ehr/pds.txt)), [Hospital](https://github.com/arjungmenon/Cassandra-to-Python/blob/master/ehr/hospital.txt) and Registration Authority ([RA](https://github.com/arjungmenon/Cassandra-to-Python/blob/master/ehr/ra.txt)). Each covers a different aspect of the NHS EHR system.

The following figure (3.1) from page 30 Moritz Becker’s thesis gives an overview of the components that constitute a *Cassandra* system:

![Figure 3.1 from Moritz Becker's thesis](https://raw.github.com/arjungmenon/Cassandra-to-Python/master/figure-3.1-cassandra-components.png)

The main goal of this project was to translate the core set of rules that determine what the user can do and who is authorized (which constitutes the *Policy component* in the figure above) into Python and to reorganize and remodel them into an object-oriented imperative form, *automatically*. Becker closely followed the requirements set forth by the NHS for their EHR while writing these policy rules. A complete listing of these policy rules can be found in Appendix A in Mortiz Y. Becker’s Dissertation under the title “Policy rules for NHS electronic health record system” or in the `ehr` folder.

Cassandra, the Language
-----------------------

The Cassandra language is a derivative of Datalog, which itself is a subset of Prolog. It is recommended readers who are unfamiliar with Prolog or Datalog, read up on the language before continuing. Datalog is a limited version Prolog, and it disallows most forms of computation; ensuring that queries in Datalog can be evaluated in polynomial time. The key issue with using *Turing-complete* languages for something like an access control policy is that there is no guarantee on the termination of program written in a Turing complete language. Not only do we need a guarantee of termination while evaluating policy rules for an RBAC system, we also need a guarantee that it will be computed in a reasonable amount of time.

Mortiz Becker adapted the Datalog language to his needs, enhancing it with two new key features that rendered them much more powerful: parameterized roles and constraints. The RBAC rules in Cassandra rules are defined in the form of [horn clauses](https://en.wikipedia.org/wiki/Horn_clause). However unlike vanilla Datalog, where atoms are of the form “a” or “b”, in Cassandra atoms can be parametrized into the form “a(p,q,r)” or “b(m,n,r)”. Parameterization reduces the amount of code required to express complex rules and increases the clarity of the rules themselves.

The second addition Becker made to Datalog are **constraints**. Constraints introduce a limited form of computation into the language. In *Cassandra*, a constraint is a predicate (usually appearing at the end of the horn clause), and it imposes mathematical constraint on variables appearing anywhere else in the horn clause. The kinds of constraints that can be imposed are equality, inequality, greater-than, less-than and membership in a range or a set. This piece of code from the Spine EHR module shows a *Cassandra* rule that is used to check if a user can activate the `Spine-clinician` role (the user is bound to the ‘cli’ atom in the rule) with a constraint that checks if the current time falls within a certain range:

	(S1.1.1)
	canActivate(cli, Spine-clinician(ra, org, spcty)) <-
	ra.hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end)),
	canActivate(ra, Registration-authority()),
	no-main-role-active(cli),
	Current-time() in [start, end]

Another addition Becker made to Datalog, to allow for the access of predicates and credentials on other entities (over the network if necessary) can be seen in the rule above. The `ra.` preceding `hasActivated` makes it a remote atom – one that needs to be accessed from the Registration Authority (RA) entity. Further description of the Cassandra language and its guarantees on computational complexity and termination can be found in *chapters 4 and 5* of [Becker’s dissertation](http://www.cs.sunysb.edu/~stoller/cse592/becker05cassandra-thesis.pdf).

The Translator
--------------

The translator is a Python program itself and it was written using version 3.2 of Python. It takes as its input four files; each file containing a set of rules corresponding to each of the four EHR modules mentioned earlier – Spine, PDS, Hospital and
RA. The can be found under the folder `ehr`, named as `spine.txt`, `pds.txt`, `hospital.txt` and `ra.txt`. When executed, the translator generates four corresponding Python source files in the `ehr` folder with the same names but with the ‘.py’ extension. Each of these four Python source files is a translation of the corresponding Cassandra
EHR rule set.

One of the goals of the translator besides simply generating equivalent Python code, was to re-model the EHR into an object-oriented structure. There were many patterns in Becker’s EHR implementation that Annie and myself had noticed, and one of the goals with the translation was to re-organize the rules into an object-oriented form. The translator sweeps through the set of rules and detects key patterns and forms new data structures based on these patterns; and eventually turns them into Python code.

Two libraries that the translator uses are:

- The [Toy Parser Generator](http://cdsoft.fr/tpg/) (TPG) by Christophe DeLord – for building an AST ([Abstract Syntax Tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree)) of the EHR rules.
- The [Typecheck](http://code.activestate.com/recipes/572161/) recipe by Dmitry Dvoinikov – I found this online while googling for library that added run-time type checking to Python using Py3k's new nifty function annotations feature.

TPG is an easy-to-use parser generator for Python that Annie and her PhD student Tom Rothamel (who taught me) have used in the instruction of the class CSE 307. Despite it's name, it's a powerful parser generator, and it's simplicity and ease-of-use make it a time-saver. The `ehrparse.py` module, which uses TPG to parse the EHR and generate the AST, was not by written by me. I believe it was written by one of Annie Liu’s graduate students. I've modified slightly though to change the structure of the AST a bit.

One thing that I don't really like about Python is [duck typing](https://en.wikipedia.org/wiki/Duck_typing) (I think it's lame) –  which is why I decided to have atleast runtime type checking, and Py3k's function annotations let you accomplish this in a rather elegant and natural manner. In addition, Dmitry's typechecking recipe is quite powerful - it's even got the ability to write lambdas that test complex constraints on arguments. The type checking has helped me catch off-hand bugs quickly that I otherwise would have spent scratching my head on.

Most of the actual translator is enclosed within the `translator` package/folder here. It contains a few modules that perform the translation on a step-by-step basis. `HypothesesTranslator.py` performs the hard and challenging task of turning the preicates in the rules into imperative executable python code. The others do more or less what their respective names indicate.

Paper Abstract
--------------
__Improving the Specification and Implementation of EHR Policy Rules__

[Arjun G. Menon](http://arjungmenon.com/) and [Yanhong A. Liu](http://www.cs.sunysb.edu/~liu/)

Trust management policies are essential in decentralized systems in general and health care systems in particular, to preserve privacy of information and control access to resources.  [Moritz Becker's dissertation](http://www.cs.sunysb.edu/~stoller/cse592/becker05cassandra-thesis.pdf) [1] describes a system for distributed role-based access control for the UK's Electronic Health Record (EHR) service. In this system, sensitive user data and resources at every node in the network of hospitals and clinics are protected by certain entities which form a "protective layers" around those resources and controls access to them based on a policy defined using a policy definition language called Cassandra. Cassandra is a high-level logic rule language based on Datalog with constraints. The expressiveness of particular rules in Cassandra can be fine tuned by means of constraints.

While this national EHR policy in Cassandra is the largest of its kind that has been formally specified, it has two main aspects that need improvements.  The policy deals with all requirements concerning access control of patient-identifiable data, including legitimate relationships, patients restricting access, authenticated express consent, third-party consent, and workgroup management.  However, with a total of 375 rules in about 2000 lines of Cassandra, the entire policy was written as flat rules, because Cassandra does not support any organizing structure.   Also, all updates are encoded as two predicates that need special processing outside the logic framework, because Cassandra does not support explicit update operations.

Our work presents a translation of the EHR policy rules from Cassandra to Python, an object-oriented programming language that supports high-level queries and updates.  Our object-oriented modeling overcomes the lack of modularity and update abilities in Cassandra.  It improves the extensibility and readability of the rules and at the same time leads to a fully executable policy specification, which can be used as a prototype for automatic policy enforcement as well as for testing and experiments.  The main challenges were to add structures to the flat policy rules in Cassandra and to make implicit updates explicit.

To assist in the translation, we developed a tool that automatically translates a large part of the EHR specification from Cassandra to Python.  The translation looks for related rules based on what roles are activated and deactivated by the rules,  and places them within role classes in the translated object-oriented model for the policy. It also translates the logic rules into high-level queries and updates over objects and sets as much as possible. The translator can automatically translate 90% of the policy rules from Cassandra to Python, leaving a few untranslated rules marked out for human translation. The rules left untranslated are complex rules that involve large nested tuple data structures that need to be re-organized and placed in separate classes.

The translated EHR policy is organized into four modules----Spine, Patient Demographic Service, Hospital, and Hospital's Registration Authority----based on the numbering of the rules expressed in Cassandra.  These modules better model the four different components of the EHR service.  A class is created for each role, for a total of 58 parameterized roles in the EHR policy, including 25 in Spine, 7 in Patient Demographic Service, 31 in Hospital, and 7 in Hospital's Registration Authority.  The parameters of the roles are naturally expressed as attributes of the corresponding role classes.  The total number of methods in the resulting object-oriented model of the EHR policy is basically  the same as the number of rules.

Overall, this work provides important improvements to this large EHR policy that allow it to be executed easily and used for functionality testing, correctness validation, and performance evaluation.

[1]  Moritz Y. Becker, Cassandra: flexible trust management and its application to electronic health records. Ph.D. Dissertation, University of Cambridge, Trinity College,
October 2005.

[Arjun G. Menon](http://arjungmenon.com/) is an alumnus of Stony Brook University who majored in Computer Science.  
[Y. Annie Liu](http://www.cs.sunysb.edu/~liu/) is a Professor in [Computer Science at Stony Brook University](http://www.cs.sunysb.edu/).
