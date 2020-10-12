from pathlib import Path
import pylexibank
import attr

from csvw.dsv import UnicodeWriter
from pytsammalex.gbif import GBIF
from pytsammalex import lexibank

# Customize your basic data.
# if you need to store other data in columns than the lexibank defaults, then over-ride
# the table type (pylexibank.[Language|Lexeme|Concept|Cognate|]) and add the required columns e.g.
#
#import attr
#
@attr.s
class Taxon(lexibank.Taxon):
    Description = attr.ib(default=None)


class Dataset(lexibank.Dataset):
    dir = Path(__file__).parent
    id = "tsammalexv1"
    concept_class = Taxon

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
        return
        for language in self.languages:
            args.writer.add_language(
                ID=language['ID'],
                Glottolog=language['Glottolog']
            )

        # add data
        for row in pylexibank.progressbar(data):
            # .. if you have segmentable data, replace `add_form` with `add_form_with_segments`
            # .. TODO @Mattis, when should we use add_forms_from_value() instead?
            lex = args.writer.add_form(
                Language_ID=row['Language_ID'],
                Parameter_ID=row['Parameter_ID'],
                Value=row['Word'],
                Form=row['Word'],
                Source=[row['Source']],
            )
            # add cognates -- make sure Cognateset_ID is global!
            args.writer.add_cognate(
                lexeme=lex,
                Cognateset_ID=row['Cognateset_ID']
            )
