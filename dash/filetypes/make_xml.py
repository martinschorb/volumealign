from pybdv.metadata import write_xml_metadata, write_n5_metadata, validate_attributes
import sys


def make_render_xml(path, scale_factors, resolution, unit):
    xml_path = path.replace('.n5', '.xml')

    attrs = {'channel': {'id': None}}
    attrs = validate_attributes(xml_path, attrs, setup_id=0,
                                enforce_consistency=False)

    write_xml_metadata(xml_path, path, unit, resolution,
                       is_h5=False,
                       setup_id=0, timepoint=0,
                       setup_name=None,
                       affine=None,
                       attributes=attrs,
                       overwrite=False,
                       overwrite_data=False,
                       enforce_consistency=False)
    write_n5_metadata(path, scale_factors, resolution, setup_id=0, timepoint=0, overwrite=True)


if __name__ == '__main__':

    # I don't have write permissions here
    # p = '/g/emcf/schorb/render-output/test-3D-downsampling.n5'

    # p = './test-giovanna_rigid.n5'
    
    p=sys.argv[1]
    
    scale_factors = 3 * [[2, 2, 2]]
    unit = 'micrometer'
    resolution = [0.05, 0.015, 0.015]
    make_render_xml(p, scale_factors, resolution, unit)
