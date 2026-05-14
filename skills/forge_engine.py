"""Sovereign Forge Engine for React/Tailwind component generation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ForgeRequest:
    """Input descriptor for enterprise-grade component generation."""

    component_name: str
    purpose: str
    aesthetic_notes: str = ""
    include_shadcn: bool = True


@dataclass(slots=True)
class ForgeOutput:
    """Generated file payloads for atomic-design delivery."""

    atom_component: str
    molecule_component: str
    organism_component: str


class ForgeEngine:
    """Generates Atomic Design React/Tailwind + shadcn/ui component scaffolds."""

    def generate(self, request: ForgeRequest) -> ForgeOutput:
        base_name = request.component_name.strip() or "SovereignComponent"
        atom = f"""import * as React from \"react\";
import {{ cn }} from \"@/lib/utils\";

export function {base_name}Atom({{ className, children }}: React.PropsWithChildren<{{ className?: string }}>) {{
  return (
    <div className={{cn(\"rounded-xl border border-border/70 bg-card p-3 shadow-sm\", className)}}>
      {{children}}
    </div>
  );
}}
"""
        molecule = f"""import * as React from \"react\";
import {{ Button }} from \"@/components/ui/button\";
import {{ {base_name}Atom }} from \"./{base_name}Atom\";

export function {base_name}Molecule() {{
  return (
    <{base_name}Atom className=\"space-y-3\">
      <h3 className=\"text-base font-semibold\">{request.purpose}</h3>
      <p className=\"text-sm text-muted-foreground\">{request.aesthetic_notes or 'Sovereign-generated design block'}</p>
      <Button variant=\"secondary\">Explore</Button>
    </{base_name}Atom>
  );
}}
"""
        organism = f"""import * as React from \"react\";
import {{ {base_name}Molecule }} from \"./{base_name}Molecule\";

export function {base_name}Organism() {{
  return (
    <section className=\"grid gap-4 md:grid-cols-2\" aria-label=\"{request.purpose}\">
      <{base_name}Molecule />
      <{base_name}Molecule />
    </section>
  );
}}
"""
        return ForgeOutput(atom_component=atom, molecule_component=molecule, organism_component=organism)
