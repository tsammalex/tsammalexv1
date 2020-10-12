import re

from pathlib import Path
import pylexibank
import attr

from csvw.dsv import UnicodeWriter
from pytsammalex.gbif import GBIF
from pytsammalex import lexibank
import pylexibank


@attr.s
class Taxon(lexibank.Taxon):
    Description = attr.ib(default=None)


@attr.s
class Name(pylexibank.Lexeme):
    ipa = attr.ib(default=None)
    grammatical_info = attr.ib(default=None)
    plural_form = attr.ib(default=None)
    basic_term = attr.ib(default=None)
    meaning = attr.ib(default=None)
    literal_translation = attr.ib(default=None)
    usage = attr.ib(default=None)
    linguistic_notes = attr.ib(default=None)
    related_lexemes = attr.ib(default=None)
    uses = attr.ib(default=None)
    ethnobiological_notes = attr.ib(default=None)
    comment = attr.ib(default=None)
    source = attr.ib(default=None)


class Dataset(lexibank.Dataset):
    dir = Path(__file__).parent
    id = "tsammalexv1"
    concept_class = Taxon
    lexeme_class = Name

    def cmd_download(self, args):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw_dir`, e.g.
        to download a temporary TSV file and convert to persistent CSV:

        >>> with self.raw_dir.temp_download("http://www.example.com/e.tsv", "example.tsv") as data:
        ...     self.raw_dir.write_csv('template.csv', self.raw_dir.read_csv(data, delimiter='\t'))
        """

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.

        A `pylexibank.cldf.LexibankWriter` instance is available as `args.writer`. Use the methods
        of this object to add data.
        """
        descs = {
            r['id']: r['characteristics'] for r in
            self.raw_dir.read_csv('taxa.csv', dicts=True)
        }
        for concept in self.concepts:
            args.writer.add_concept(Description=descs[concept['ID']], **concept)

        # TODO: add media!

        for language in self.raw_dir.read_csv('languages.csv', dicts=True):
            args.writer.add_language(
                ID=language['id'],
                Name=language['name'],
                Glottocode=language['glottocode'],
                Latitude=language['latitude'],
                Longitude=language['longitude'],
            )

        args.writer.add_sources()

        args.writer.cldf['FormTable', 'uses'].separator = ';'
        uses = {r['id']: r['name'] for r in self.raw_dir.read_csv('uses.csv', dicts=True)}
        for row in self.raw_dir.read_csv('names.csv', dicts=True):
            refs = [s.replace('[]', '') for s in re.split('(?<=])[,;]\s*', row['refs__ids'])]
            args.writer.add_form(
                Language_ID=row['languages__id'],
                Parameter_ID=row['taxa__id'],
                Value=row['name'],
                Form=row['name'],
                Source=refs,
                uses=[uses[u] for u in re.split('[,;]\s', row['uses__ids']) if u],
                **{k: row[k] for k in attr.fields_dict(Name) if k in row and row[k]}
            )
        self.add_image_schema(args.writer)
        cdstar = self.raw_dir.read_json('cdstar.json')
        for row in self.raw_dir.read_csv('images.csv', dicts=True):
            args.writer.objects['images.csv'].append(dict(
                ID=row['id'],
                Taxon_ID=row['taxa__id'],
                objid=cdstar[row['id']]['objid'],
                bitsreamid=cdstar[row['id']]['original'],
                tags=row['tags'].split(';'),
                **{k: v for k, v in row.items()
                   if k in ['mime_type', 'creator', 'date', 'place', 'permission', 'source']}
            ))
