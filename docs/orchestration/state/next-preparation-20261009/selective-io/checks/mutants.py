import sys
src=open(sys.argv[1]).read(); k=sys.argv[2]
M={
"M1-no-verify-at-first-entry":("        self.verify()\n        self.GetEntry = self._tree.GetEntry","        self.GetEntry = self._tree.GetEntry"),
"M2-no-inactive-check":("        if not self._tree.GetBranchStatus(name):\n            raise","        if False:\n            raise"),
"M3-no-status-restore":("        restore_branch_status(tree, snapshot)\n        restore_branch_addresses","        restore_branch_addresses"),
"M4-default-applies-selection":('    if branch_select == "all":\n        return func(tree, *args, **kwargs)\n','    if branch_select == "all":\n        branch_select = "derived"\n'),
"M5-rule-forgets-alt":("        if use_w and alt is not None:\n","        if False:\n"),
"M6-no-address-restore":("        restore_branch_addresses(tree, addresses)\n","        pass\n"),
}
old,new=M[k]; assert src.count(old)==1,k
open(sys.argv[1],"w").write(src.replace(old,new))
