from typing import Tuple
from bs4 import Tag

def __parse_style_attribute(style_attribute: str) -> dict:
    declarations = [declaration.strip() for declaration in style_attribute.split(';') if declaration]
    return {property_name : value for property_name, value in map(__split_declaration, declarations)}

def __split_declaration(declaration: str) -> Tuple[str, str]:
    declaration_parts = declaration.split(':', 1)
    property_name = declaration_parts[0].strip()
    value = declaration_parts[1].strip() if len(declaration_parts) > 1 else ''
    return property_name, value

def get_attributes(tag: Tag) -> dict:
    attributes = tag.attrs
    if 'style' in attributes:
        attributes['style'] = __parse_style_attribute(tag.get('style'))
    return attributes