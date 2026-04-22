"""Schema helper types for `addressbook.capnp`."""

from . import modules as modules

type _AddressBookSchema = modules._AddressBookStructModule._AddressBookSchema

type _PersonPersonEmploymentSchema = modules._PersonStructModule._PersonEmploymentStructModule._PersonEmploymentSchema

type _PersonPersonTestGroupSchema = modules._PersonStructModule._PersonTestGroupStructModule._PersonTestGroupSchema

type _PersonPhoneNumberSchema = modules._PersonStructModule._PhoneNumberStructModule._PhoneNumberSchema

type _PersonSchema = modules._PersonStructModule._PersonSchema
