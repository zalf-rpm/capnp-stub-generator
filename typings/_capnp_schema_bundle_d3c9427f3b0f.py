"""Private compiled schema bundle for generated capnp modules."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

import capnp

import schema_capnp

if TYPE_CHECKING:
    from capnp.lib.capnp import _DynamicStructReader, _Schema

capnp.remove_import_hook()

_SCHEMA_NODES = [
    (
        0x934EFEA7F017FFF0,
        "EBxQBgb/8P8X8Kf+TpMAARgAAxEV8hEhNwAD/2FkZHJlc3NiAm9vay9hZGRyZXNzYm9vay4fY2FwbnBRDAEB/3np4RPaWnGkABERIv+oqbKqadtnpgARDTr/F12NYB041N4AEQliB3F1eD9QZXJzb27/QWRkcmVzc0IAB29vaw==",
    ),  # addressbook/addressbook.capnp
    (
        0xA4715ADA13E1E979,
        "EBpQBgb/eenhE9pacaQAER4E//D/F/Cn/k6TAAABERYuMRUSARElBwAAUSADAVEsAgEAAP9hZGRyZXNzYgNvb2svYWRkcmVzc2Jvb2suY2FwbnA6cXUBeFABAQEIAAIRCHsAAQ==",
    ),  # addressbook/addressbook.capnp:qux
    (
        0xA667DB69AAB2A9A8,
        "EHpQBgb/qKmyqmnbZ6YAUR4BA//w/xfwp/5OkwAFBQcAADEwRAIxFSoBESUXAAAxMY8BAAH/YWRkcmVzc2IDb29rL2FkZHJlc3Nib29rLmNhcG5wOlBlD3Jzb25RBAEB/4upZV3MHMn2ABEBYv9QaG9uZU51bQAHYmVyURwDBAAABAEAABG1GgAAUbADAVG8AgEBARQBAQAAEbkqAABRtAMBUcACARECARQBAgAAEb0yAABRuAMBUcQCAREDAhQBAwAAEcE6AABRvAMBUdgCAQEEAQH/Wl/LUsayUboAEdVaAAIBBQEB/6w0IdDpRMOYABHBUgACEQYEFAELAAARrVIAAFGsAwFRuAIBA2lkAQgAAgEIAAEPbmFtZQEMAAIBDAABH2VtYWlsAQwAAgEMAAE/cGhvbmVzAQ4AAVADAQEQ/4upZV3MHMn2AAABAQ4AAf9lbXBsb3ltZQADbnT/dGVzdEdyb3UAAXD/ZXh0cmFEYXQAAWEBDQACAQ0AAQ==",
    ),  # addressbook/addressbook.capnp:Person
    (
        0xF6C91CCC5D65A98B,
        "EDdQBgb/i6llXcwcyfYAUSUBAf+oqbKqadtnpgAFAQcAADGXHQExFYoBES0XAAARNXcAAf9hZGRyZXNzYgVvb2svYWRkcmVzc2Jvb2suY2FwbnA6UGVyc29uLlBob25lTnVtYmVyAABRBAEB/8cl+Qbkk2ChABEBKg9UeXBlUQgDBAAABAEAABEpOgAAUSQDAVEwAgEBARQBAQAAES0qAABRKAMBUTQCAT9udW1iZXIBDAACAQwAAQ90eXBlAQ//xyX5BuSTYKEAAAEBDwAB",
    ),  # addressbook/addressbook.capnp:Person.PhoneNumber
    (
        0xA16093E406F925C7,
        "ECJQBgb/xyX5BuSTYKEAETEC/4upZV3MHMn2AAABMdkZATEVsgERLQcAABEpTwAB/2FkZHJlc3NiBW9vay9hZGRyZXNzYm9vay5jYXBucDpQZXJzb24uUGhvbmVOdW1iZXIfLlR5cGVQAQFRDAECAAARHToAAAEBERUqAAABAhENKgAAP21vYmlsZQ9ob21lD3dvcms=",
    ),  # addressbook/addressbook.capnp:Person.PhoneNumber.Type
    (
        0xBA51B2C652CB5F5A,
        "EFNQBgb/Wl/LUsayUboAUSUBA/+oqbKqadtnpgBVBQcBBAECAAAxFYIBAAERIecAAf9hZGRyZXNzYgVvb2svYWRkcmVzc2Jvb2suY2FwbnA6UGVyc29uLmVtcGxveW1lbnQAURADBAz//xQBBAAAEWFaAABRYAMBUWwCAR0B/v8DFAEFAAARaUoAAFFoAwFRdAIBHQL9/wMUAQYAABFxOgAAUWwDAVF4AgENA/z/FAEHAAARdWoAAFF0AwFRgAIB/3VuZW1wbG95AANlZAAG/2VtcGxveWVyAAAAAQwAAgEMAAE/c2Nob29sAQwAAgEMAAH/c2VsZkVtcGwAD295ZWQABg==",
    ),  # addressbook/addressbook.capnp:Person.employment
    (
        0x98C344E9D02134AC,
        "EEFQBgb/rDQh0OlEw5gAUSUBA/+oqbKqadtnpgAVBQcBAAExFXoBAAERIa8AAf9hZGRyZXNzYgRvb2svYWRkcmVzc2Jvb2suY2FwbnA6UGVyc29uLnRlcz90R3JvdXBRDAMEEAIUAQgAABFFOgAAUUADAVFMAgERAQMUAQkAABFJOgAAUUQDAVFQAgERAgQUAQoAABFNOgAAUUgDAVFUAgE/ZmllbGQxAQgAAgEIAAE/ZmllbGQyAQgAAgEIAAE/ZmllbGQzAQgAAgEIAAE=",
    ),  # addressbook/addressbook.capnp:Person.testGroup
    (
        0xDED4381D608D5D17,
        "EChQBgb/F12NYB041N4AER4B//D/F/Cn/k6TAAUBBwAAM0YCdwIxFVIBESkHAAARJT8AAf9hZGRyZXNzYgRvb2svYWRkcmVzc2Jvb2suY2FwbnA6QWRkcmVzc0JvbwFrUAEBUQQDBAAABAEAABENOgAAUQgDAVEkAgE/cGVvcGxlAQ4AAVADAQEQ/6ipsqpp22emAAABAQ4AAQ==",
    ),  # addressbook/addressbook.capnp:AddressBook
    (
        0x85150B117366D14B,
        "EBZQBgb/S9FmcxELFYUAARYAAxEV4hEhFwAD/2NhbGN1bGF0Am9yL2NhbGN1bGF0b3IuY2EHcG5wUQQBAf82zDXfkjOYlwARAVr/Q2FsY3VsYXQAA29y",
    ),  # calculator/calculator.capnp
    (
        0x97983392DF35CC36,
        "EEVQBgb/Nsw135IzmJcAERwD/0vRZnMRCxWFAAABMRaZDTEVOgERJUcAABFdxxHhBwAA/2NhbGN1bGF0A29yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsYz91bGF0b3JREAEB/xWNVPXK1zjUABEZWv/SSO7TNJ3mwwARGTL/lAOElj066O0AERVK/+bf5mF4QJOHABEVSv9FeHByZXNzaQADb24fVmFsdWX/RnVuY3Rpb24AAAD/T3BlcmF0b3IAAABRDAMFAAD/1DZ6VeGqDrsBEaaHWPWjsYERUUoAAhFJBwEB/4ncVkW6vIfyAcjWfARl9CSNET1iAAIRNQcBAv8wxaP0tM6NigEgjMBjd7uP0REpYgACESEH/2V2YWx1YXRlAAAAQAH/ZGVmRnVuY3QAB2lvbkAB/2dldE9wZXJhAAd0b3JAAVABAQ==",
    ),  # calculator/calculator.capnp:Calculator
    (
        0xD438D7CAF5548D15,
        "EE1QBgb/FY1U9crXONQAUScBAv82zDXfkjOYlwBFAgcEAQQz2gXeBzEVkgERLQcAABEp5wAB/2NhbGN1bGF0BW9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5FeHByZXNzaW8BblABAVEQAwQM//8EAQAAEWFCAABRXAMBUWgCAQ0B/v8UAQEAABFlegAAUWQDAVFwAgENAv3/FAECAAARbVIAAFFsAwFReAIBDQP8/wEB/2aNh9OjIpXZABF1KgACf2xpdGVyYWwBCwACAQsAAf9wcmV2aW91cwA/UmVzdWx0ARH/0kju0zSd5sMAAAEBEQAB/3BhcmFtZXRlAAFyAQgAAgEIAAEPY2FsbA==",
    ),  # calculator/calculator.capnp:Calculator.Expression
    (
        0xC3E69D34D3EE48D2,
        "ECBQBgb/0kju0zSd5sMAEScD/zbMNd+SM5iXAAABM+IHEQkxFWoBESkHAAARJUcRTQcAAP9jYWxjdWxhdARvci9jYWxjdWxhdG9yLmNhcG5wOkNhbGN1bGF0b3IuVg9hbHVlUAEBUQQDBQAA/1i1jdV0JVPTASLoKhIjZ77mEREqAAIRBQcPcmVhZEABUAEB",
    ),  # calculator/calculator.capnp:Calculator.Value
    (
        0xD3532574D58DB558,
        "EBVQBgb/WLWN1XQlU9MAES0BAAAEBwABMRXKAQAE/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5WYWx1ZS5yZWFkJFBhcmFtcwAA",
    ),  # calculator/calculator.capnp:Calculator.Value.read$Params
    (
        0xE6BE6723122AE822,
        "ECVQBgb/IugqEiNnvuYAUS0BAQAABAcAATEV0gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5WYWx1ZS5yZWFkJFJlc3VsdAFzUQQDBAAABAEAABENMgAAUQgDAVEUAgEfdmFsdWUBCwACAQsAAQ==",
    ),  # calculator/calculator.capnp:Calculator.Value.read$Results
    (
        0xD99522A3D3878D66,
        "EDhQBgb/Zo2H06MildkAUTIBAv8VjVT1ytc41AAVAgcBAAExFboBAAERJXcAAf9jYWxjdWxhdAVvci9jYWxjdWxhdG9yLmNhcG5wOkNhbGN1bGF0b3IuRXhwcmVzc2lvP24uY2FsbFEIAwQAABQBAwAAESlKAABRKAMBUTQCAREBARQBBAAAETE6AABRLAMBUUgCAf9mdW5jdGlvbgAAAAER/5QDhJY9OujtAAABAREAAT9wYXJhbXMBDgABUAMBARD/FY1U9crXONQAAAEBDgAB",
    ),  # calculator/calculator.capnp:Calculator.Expression.call
    (
        0xEDE83A3D96840394,
        "ECBQBgb/lAOElj066O0AEScD/zbMNd+SM5iXAAABM/cJqgwxFYIBESkHAAARJUcRTQcAAP9jYWxjdWxhdAVvci9jYWxjdWxhdG9yLmNhcG5wOkNhbGN1bGF0b3IuRnVuY3Rpb24AUAEBUQQDBQAA/xd3uHDfYJGxAa3eFGn3q+DAEREqAAIRBQcPY2FsbEABUAEB",
    ),  # calculator/calculator.capnp:Calculator.Function
    (
        0xB19160DF70B87717,
        "EClQBgb/F3e4cN9gkbEAETABAAAFAQcAATEV4gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5GdW5jdGlvbi5jYWxsJFBhcgdhbXNRBAMEAAAEAQAAEQ06AABRCAMBUSQCAT9wYXJhbXMBDgABUAMBAQsAAgEOAAE=",
    ),  # calculator/calculator.capnp:Calculator.Function.call$Params
    (
        0xC0E0ABF76914DEAD,
        "ECVQBgb/rd4Uafer4MAAUTABAQAABAcAATEV6gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5GdW5jdGlvbi5jYWxsJFJlcw91bHRzUQQDBAAABAEAABENMgAAUQgDAVEUAgEfdmFsdWUBCwACAQsAAQ==",
    ),  # calculator/calculator.capnp:Calculator.Function.call$Results
    (
        0x8793407861E6DFE6,
        "ECdQBgb/5t/mYXhAk4cAEScC/zbMNd+SM5iXAAABM0cNlw0xFYIBESkHAAARJWcAAf9jYWxjdWxhdAVvci9jYWxjdWxhdG9yLmNhcG5wOkNhbGN1bGF0b3IuT3BlcmF0b3IAUAEBURABAgAAESkiAAABAREhSgAAAQIRHUoAAAEDERk6AAAHYWRk/3N1YnRyYWN0AAAA/211bHRpcGx5AAAAP2RpdmlkZQ==",
    ),  # calculator/calculator.capnp:Calculator.Operator
    (
        0xBB0EAAE1557A36D4,
        "ECVQBgb/1DZ6VeGqDrsAEScBAAAFAQcAATEVugEAARElPwAB/2NhbGN1bGF0BW9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5ldmFsdWF0ZSQ/UGFyYW1zUQQDBAAABAEAABENWgAAUQwDAVEYAgH/ZXhwcmVzc2kAA29uARD/FY1U9crXONQAAAEBEAAB",
    ),  # calculator/calculator.capnp:Calculator.evaluate$Params
    (
        0x81B1A3F55887A611,
        "ECRQBgb/EaaHWPWjsYEAEScBAAAFAQcAATEVwgEAARElPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5ldmFsdWF0ZSRSZXN1bHRzAFEEAwQAAAQBAAARDTIAAFEIAwFRFAIBH3ZhbHVlARH/0kju0zSd5sMAAAEBEQAB",
    ),  # calculator/calculator.capnp:Calculator.evaluate$Results
    (
        0xF287BCBA4556DC89,
        "EDVQBgb/idxWRbq8h/IAUScBAQAABQEHAAExFdIBAAERKXcAAf9jYWxjdWxhdAZvci9jYWxjdWxhdG9yLmNhcG5wOkNhbGN1bGF0b3IuZGVmRnVuY3Rpb24kUGFyYW0Bc1EIAwQAAAQBAAARKVoAAFEoAwFRNAIBAQEUAQEAABExKgAAUSwDAVE4AgH/cGFyYW1Db3UAA250AQQAAgEEAAEPYm9keQEQ/xWNVPXK1zjUAAABARAAAQ==",
    ),  # calculator/calculator.capnp:Calculator.defFunction$Params
    (
        0x8D24F465047CD6C8,
        "ECVQBgb/yNZ8BGX0JI0AEScBAAAFAQcAATEV2gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5kZWZGdW5jdGlvbiRSZXN1bAN0c1EEAwQAAAQBAAARDSoAAFEIAwFRFAIBD2Z1bmMBEf+UA4SWPTro7QAAAQERAAE=",
    ),  # calculator/calculator.capnp:Calculator.defFunction$Results
    (
        0x8A8DCEB4F4A3C530,
        "ECVQBgb/MMWj9LTOjYoAUScBAQAABAcAATEV0gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5nZXRPcGVyYXRvciRQYXJhbQFzUQQDBAAABAEAABENGgAAUQgDAVEUAgEDb3ABD//m3+ZheECThwAAAQEPAAE=",
    ),  # calculator/calculator.capnp:Calculator.getOperator$Params
    (
        0xD18FBB7763C08C20,
        "ECVQBgb/IIzAY3e7j9EAEScBAAAFAQcAATEV2gEAAREpPwAB/2NhbGN1bGF0Bm9yL2NhbGN1bGF0b3IuY2FwbnA6Q2FsY3VsYXRvci5nZXRPcGVyYXRvciRSZXN1bAN0c1EEAwQAAAQBAAARDSoAAFEIAwFRFAIBD2Z1bmMBEf+UA4SWPTro7QAAAQERAAE=",
    ),  # calculator/calculator.capnp:Calculator.getOperator$Results
    (
        0x9876543210ABCDF1,
        "EBxQBgb/8c2rEDJUdpgAARIAAxEVwhEdNwAD/3Jlc3RvcmVyAi9yZXN0b3Jlci5jYXBucABRDAEB/+32VV8MfNGYABERIv+Ts+QdgP3F1QARDUr/ZuOu7GhISo0AEQ1SB0JhZ/9SZXN0b3JlcgAAAP9BbnlUZXN0ZQABcg==",
    ),  # restorer/restorer.capnp
    (
        0x98D17C0C5F55F6ED,
        "ECpQBgb/7fZVXwx80ZgAERgD//HNqxAyVHaYAAABERaYERXiESEHAAARHYcRdQcAAP9yZXN0b3JlcgIvcmVzdG9yZXIuY2FwbnA6B0JhZ1ABAVEIAwUAAP8ZIzcsKrijwAGCCbHB0gaB4BExSgACESkHAQH/zPH8ARX1RbUBFbuRiFg5o/IRHUoAAhEVB/9nZXRWYWx1ZQAAAEAB/3NldFZhbHVlAAAAQAFQAQE=",
    ),  # restorer/restorer.capnp:Bag
    (
        0xC0A3B82A2C372319,
        "EBNQBgb/GSM3LCq4o8AAERwBAAAEBwABMRViAQAE/3Jlc3RvcmVyBC9yZXN0b3Jlci5jYXBucDpCYWcuZ2V0VmFsdWUkUGFyB2Ftcw==",
    ),  # restorer/restorer.capnp:Bag.getValue$Params
    (
        0xE08106D2C1B10982,
        "ECNQBgb/ggmxwdIGgeAAERwBAAAFAQcAATEVagEAAREhPwAB/3Jlc3RvcmVyBC9yZXN0b3Jlci5jYXBucDpCYWcuZ2V0VmFsdWUkUmVzD3VsdHNRBAMEAAAEAQAAEQ0yAABRCAMBURQCAR92YWx1ZQEMAAIBDAAB",
    ),  # restorer/restorer.capnp:Bag.getValue$Results
    (
        0xB545F51501FCF1CC,
        "ECNQBgb/zPH8ARX1RbUAERwBAAAFAQcAATEVYgEAAREhPwAB/3Jlc3RvcmVyBC9yZXN0b3Jlci5jYXBucDpCYWcuc2V0VmFsdWUkUGFyB2Ftc1EEAwQAAAQBAAARDTIAAFEIAwFRFAIBH3ZhbHVlAQwAAgEMAAE=",
    ),  # restorer/restorer.capnp:Bag.setValue$Params
    (
        0xF2A339588891BB15,
        "EBNQBgb/FbuRiFg5o/IAERwBAAAEBwABMRVqAQAE/3Jlc3RvcmVyBC9yZXN0b3Jlci5jYXBucDpCYWcuc2V0VmFsdWUkUmVzD3VsdHM=",
    ),  # restorer/restorer.capnp:Bag.setValue$Results
    (
        0xD5C5FD801DE4B393,
        "EC5QBgb/k7PkHYD9xdUAERgD//HNqxAyVHaYAAABMZq7ATEVCgERJRcAABExhxGFBwAA/3Jlc3RvcmVyAy9yZXN0b3Jlci5jYXBucDpSZXN0b3JlcgAAUQQBAf+I533fUlHa1AARAXL/UmVzdG9yZVAAH2FyYW1zUQgDBQAA/4jnfd9SUdrUAQ6Rh2SC/S67ETFCAAIRJQcBAf+w0PDrVEtD0wGrfICBYSP1tBEZagACEREHf3Jlc3RvcmVAAf9nZXRBbnlUZQAPc3RlckABUAEB",
    ),  # restorer/restorer.capnp:Restorer
    (
        0xD4DA5152DF7DE788,
        "ECVQBgb/iOd931JR2tQAESEB/5Oz5B2A/cXVAAUBBwAAMd0OATEVegERKQcAABElPwAB/3Jlc3RvcmVyBC9yZXN0b3Jlci5jYXBucDpSZXN0b3Jlci5SZXN0b3JlP1BhcmFtc1ABAVEEAwQAAAQBAAARDUoAAFEMAwFRGAIB/2xvY2FsUmVmAAAAAQwAAgEMAAE=",
    ),  # restorer/restorer.capnp:Restorer.RestoreParams
    (
        0xBB2EFD826487910E,
        "ECRQBgb/DpGHZIL9LrsAESEBAAAFAQcAATEVigEAARElPwAB/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpSZXN0b3Jlci5yZXN0b3JlJFJlc3VsdHMAAFEEAwQAAAQBAAARDSIAAFEIAwFRFAIBB2NhcAESBAMAAQESAAE=",
    ),  # restorer/restorer.capnp:Restorer.restore$Results
    (
        0xD3434B54EBF0D0B0,
        "EBRQBgb/sNDw61RLQ9MAESEBAAAEBwABMRWqAQAE/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpSZXN0b3Jlci5nZXRBbnlUZXN0ZXIkUGEPcmFtcw==",
    ),  # restorer/restorer.capnp:Restorer.getAnyTester$Params
    (
        0xB4F5236181807CAB,
        "ECRQBgb/q3yAgWEj9bQAESEBAAAFAQcAATEVsgEAARElPwAB/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpSZXN0b3Jlci5nZXRBbnlUZXN0ZXIkUmUfc3VsdHNRBAMEAAAEAQAAEQ06AABRCAMBURQCAT90ZXN0ZXIBEf9m467saEhKjQAAAQERAAE=",
    ),  # restorer/restorer.capnp:Restorer.getAnyTester$Results
    (
        0x8D4A4868ECAEE366,
        "EEFQBgb/ZuOu7GhISo0AERgD//HNqxAyVHaYAAABM70BdAIxFRIBESUHAAAxIQcBEdEHAAD/cmVzdG9yZXIDL3Jlc3RvcmVyLmNhcG5wOkFueVRlc3RlAXJQAQFREAMFAAD/cwUPF904R/4BDXduw2jWKvQRcWoAAhFpBwEB/+RtNPtP9+yjAZt094WszVqqEV1aAAIRVQcBAv+hxyK+IElBiwGUNYEtIfDPsxFJcgACEUEHAQP/VbI9oj7+CP8BPGhdKea/JugRNXIAAhEtB/9nZXRBbnlTdAAPcnVjdEAB/2dldEFueUxpAANzdEAB/2dldEFueVBvAB9pbnRlckAB/3NldEFueVBvAB9pbnRlckABUAEB",
    ),  # restorer/restorer.capnp:AnyTester
    (
        0xFE4738DD170F0573,
        "EBRQBgb/cwUPF904R/4AESIBAAAEBwABMRWyAQAE/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55U3RydWN0JFAfYXJhbXM=",
    ),  # restorer/restorer.capnp:AnyTester.getAnyStruct$Params
    (
        0xF42AD668C36E770D,
        "ECRQBgb/DXduw2jWKvQAESIBAAAFAQcAATEVugEAARElPwAB/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55U3RydWN0JFI/ZXN1bHRzUQQDBAAABAEAABENEgAAUQgDAVEUAgEBcwESBAEAAQESAAE=",
    ),  # restorer/restorer.capnp:AnyTester.getAnyStruct$Results
    (
        0xA3ECF74FFB346DE4,
        "EBRQBgb/5G00+0/37KMAESIBAAAEBwABMRWiAQAE/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55TGlzdCRQYXIHYW1z",
    ),  # restorer/restorer.capnp:AnyTester.getAnyList$Params
    (
        0xAA5ACDAC85F7749B,
        "ECRQBgb/m3T3hazNWqoAESIBAAAFAQcAATEVqgEAARElPwAB/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55TGlzdCRSZXMPdWx0c1EEAwQAAAQBAAARDRIAAFEIAwFRFAIBAWwBEgQCAAEBEgAB",
    ),  # restorer/restorer.capnp:AnyTester.getAnyList$Results
    (
        0x8B414920BE22C7A1,
        "EBRQBgb/occiviBJQYsAESIBAAAEBwABMRW6AQAE/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55UG9pbnRlciQ/UGFyYW1z",
    ),  # restorer/restorer.capnp:AnyTester.getAnyPointer$Params
    (
        0xB3CFF0212D813594,
        "ECRQBgb/lDWBLSHwz7MAESIBAAAFAQcAATEVwgEAARElPwAB/3Jlc3RvcmVyBi9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuZ2V0QW55UG9pbnRlciRSZXN1bHRzAFEEAwQAAAQBAAARDRIAAFEIAwFRFAIBAXABEgACARIAAQ==",
    ),  # restorer/restorer.capnp:AnyTester.getAnyPointer$Results
    (
        0xFF08FE3EA23DB255,
        "ECRQBgb/VbI9oj7+CP8AESIBAAAFAQcAATEVugEAARElPwAB/3Jlc3RvcmVyBS9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuc2V0QW55UG9pbnRlciQ/UGFyYW1zUQQDBAAABAEAABENEgAAUQgDAVEUAgEBcAESAAIBEgAB",
    ),  # restorer/restorer.capnp:AnyTester.setAnyPointer$Params
    (
        0xE826BFE6295D683C,
        "EBRQBgb/PGhdKea/JugAESIBAAAEBwABMRXCAQAE/3Jlc3RvcmVyBi9yZXN0b3Jlci5jYXBucDpBbnlUZXN0ZXIuc2V0QW55UG9pbnRlciRSZXN1bHRzAA==",
    ),  # restorer/restorer.capnp:AnyTester.setAnyPointer$Results
    (
        0x9823749823749823,
        "EBpQBgb/I5h0I5h0I5gAARoAAzEVAgERIScAA/9zaW5nbGVfdgNhbHVlL3NpbmdsZV92YWx1ZS5jYXBucABRCAEB/953UmMUzp20ABEJYv+XW9AlnoVjigARCUr/U2luZ2xlVmEAB2x1Zf9NeVN0cnVjdAAAAA==",
    ),  # single_value/single_value.capnp
    (
        0xB49DCE14635277DE,
        "EH5QBgb/3ndSYxTOnbQAESAD/yOYdCOYdCOYAAABMRahATEVYgERKQcAADElhwITxQEHAAD/c2luZ2xlX3YEYWx1ZS9zaW5nbGVfdmFsdWUuY2FwbnA6U2luZ2xlVmEHbHVlUAEBUSgDBQAA/1un8HFAvJyfAatvxfMPTbWfEzEBQgACEyUBBwEB/0v/4VFLsufhASlUKGfem46rExkBOgACEw0BBwEC/2mUdrR0EQvNAYEFxlTVqu7lEwEBSgACEfkHAQP/dHVnqj+OLIkBTlaHwpvqBbYR7UIAAhHhBwEE/4M5OHNgHFGrAZ4gdfiekGfBEdVCAAIRyQcBBf9UtLPJzJYF9gGQHwsz0TRYvBG9QgACEbEHAQb/RD+08q9hhKUB2aVm9DKAYtURpVIAAhGdBwEH/55m/sL4wOaEAXKfK7lJAonkEZFqAAIRiQcBCP+4DgYGA/xY5gH75TIfUvkK6BF9OgACEXEHAQn/dBpHfhQqSMMBouAFRUJXCbURZXIAAhFdB39nZXRCb29sQAE/Z2V0SW50QAH/Z2V0RmxvYXQAAABAAX9nZXRUZXh0QAF/Z2V0RGF0YUABf2dldExpc3RAAf9nZXRTdHJ1YwABdEAB/2dldEludGVyAA9mYWNlQAE/Z2V0QW55QAH/Z2V0TGlzdFMAH3RydWN0QAFQAQE=",
    ),  # single_value/single_value.capnp:SingleValue
    (
        0x9F9CBC4071F0A75B,
        "EBVQBgb/W6fwcUC8nJ8AESwBAAAEBwABMRXaAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEJvb2wkUGFyYQNtcw==",
    ),  # single_value/single_value.capnp:SingleValue.getBool$Params
    (
        0x9FB54D0FF3C56FAB,
        "ECVQBgb/q2/F8w9NtZ8AUSwBAQAABAcAATEV4gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEJvb2wkUmVzdQdsdHNRBAMEAAAEAQAAEQ0iAABRCAMBURQCAQd2YWwBAQACAQEAAQ==",
    ),  # single_value/single_value.capnp:SingleValue.getBool$Results
    (
        0xE1E7B24B51E1FF4B,
        "EBVQBgb/S//hUUuy5+EAESwBAAAEBwABMRXSAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEludCRQYXJhbQFz",
    ),  # single_value/single_value.capnp:SingleValue.getInt$Params
    (
        0xAB8E9BDE67285429,
        "ECVQBgb/KVQoZ96bjqsAUSwBAQAABAcAATEV2gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEludCRSZXN1bAN0c1EEAwQAAAQBAAARDSIAAFEIAwFRFAIBB3ZhbAEEAAIBBAAB",
    ),  # single_value/single_value.capnp:SingleValue.getInt$Results
    (
        0xCD0B1174B4769469,
        "EBVQBgb/aZR2tHQRC80AESwBAAAEBwABMRXiAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEZsb2F0JFBhcgdhbXM=",
    ),  # single_value/single_value.capnp:SingleValue.getFloat$Params
    (
        0xE5EEAAD554C60581,
        "ECVQBgb/gQXGVNWq7uUAUSwBAQAABAcAATEV6gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEZsb2F0JFJlcw91bHRzUQQDBAAABAEAABENIgAAUQgDAVEUAgEHdmFsAQsAAgELAAE=",
    ),  # single_value/single_value.capnp:SingleValue.getFloat$Results
    (
        0x892C8E3FAA677574,
        "EBVQBgb/dHVnqj+OLIkAESwBAAAEBwABMRXaAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldFRleHQkUGFyYQNtcw==",
    ),  # single_value/single_value.capnp:SingleValue.getText$Params
    (
        0xB605EA9BC287564E,
        "ECVQBgb/TlaHwpvqBbYAESwBAAAFAQcAATEV4gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldFRleHQkUmVzdQdsdHNRBAMEAAAEAQAAEQ0iAABRCAMBURQCAQd2YWwBDAACAQwAAQ==",
    ),  # single_value/single_value.capnp:SingleValue.getText$Results
    (
        0xAB511C6073383983,
        "EBVQBgb/gzk4c2AcUasAESwBAAAEBwABMRXaAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldERhdGEkUGFyYQNtcw==",
    ),  # single_value/single_value.capnp:SingleValue.getData$Params
    (
        0xC167909EF875209E,
        "ECVQBgb/niB1+J6QZ8EAESwBAAAFAQcAATEV4gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldERhdGEkUmVzdQdsdHNRBAMEAAAEAQAAEQ0iAABRCAMBURQCAQd2YWwBDQACAQ0AAQ==",
    ),  # single_value/single_value.capnp:SingleValue.getData$Results
    (
        0xF60596CCC9B3B454,
        "EBVQBgb/VLSzycyWBfYAESwBAAAEBwABMRXaAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldExpc3QkUGFyYQNtcw==",
    ),  # single_value/single_value.capnp:SingleValue.getList$Params
    (
        0xBC5834D1330B1F90,
        "EClQBgb/kB8LM9E0WLwAESwBAAAFAQcAATEV4gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldExpc3QkUmVzdQdsdHNRBAMEAAAEAQAAEQ0iAABRCAMBUSQCAQd2YWwBDgABUAMBAQQAAgEOAAE=",
    ),  # single_value/single_value.capnp:SingleValue.getList$Results
    (
        0xA58461AFF2B43F44,
        "EBVQBgb/RD+08q9hhKUAESwBAAAEBwABMRXqAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldFN0cnVjdCRQYQ9yYW1z",
    ),  # single_value/single_value.capnp:SingleValue.getStruct$Params
    (
        0xD5628032F466A5D9,
        "ECVQBgb/2aVm9DKAYtUAESwBAAAFAQcAATEV8gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldFN0cnVjdCRSZR9zdWx0c1EEAwQAAAQBAAARDSIAAFEIAwFRFAIBB3ZhbAEQ/5db0CWehWOKAAABARAAAQ==",
    ),  # single_value/single_value.capnp:SingleValue.getStruct$Results
    (
        0x8A63859E25D05B97,
        "ECRQBgb/l1vQJZ6FY4oAUSABAf8jmHQjmHQjmAAEBwAAM6MBxgExFUoBESkHAAARJT8AAf9zaW5nbGVfdgRhbHVlL3NpbmdsZV92YWx1ZS5jYXBucDpNeVN0cnVjdAAAUAEBUQQDBAAABAEAABENGgAAUQgDAVEUAgEDaWQBBAACAQQAAQ==",
    ),  # single_value/single_value.capnp:MyStruct
    (
        0x84E6C0F8C2FE669E,
        "EBVQBgb/nmb+wvjA5oQAESwBAAAEBwABMRUCAgAE/3NpbmdsZV92B2FsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEludGVyZmFjZSRQYXJhbXMA",
    ),  # single_value/single_value.capnp:SingleValue.getInterface$Params
    (
        0xE4890249B92B9F72,
        "ECZQBgb/cp8ruUkCieQAESwBAAAFAQcAATEVCgIAAREtPwAB/3NpbmdsZV92B2FsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEludGVyZmFjZSRSZXN1bHRzAABRBAMEAAAEAQAAEQ0iAABRCAMBURQCAQd2YWwBEf/ed1JjFM6dtAAAAQERAAE=",
    ),  # single_value/single_value.capnp:SingleValue.getInterface$Results
    (
        0xE658FC0306060EB8,
        "EBVQBgb/uA4GBgP8WOYAESwBAAAEBwABMRXSAQAE/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEFueSRQYXJhbQFz",
    ),  # single_value/single_value.capnp:SingleValue.getAny$Params
    (
        0xE80AF9521F32E5FB,
        "ECVQBgb/++UyH1L5CugAESwBAAAFAQcAATEV2gEAAREpPwAB/3NpbmdsZV92BmFsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldEFueSRSZXN1bAN0c1EEAwQAAAQBAAARDSIAAFEIAwFRFAIBB3ZhbAESAAIBEgAB",
    ),  # single_value/single_value.capnp:SingleValue.getAny$Results
    (
        0xC3482A147E471A74,
        "EBZQBgb/dBpHfhQqSMMAESwBAAAEBwABMRUKAgAE/3NpbmdsZV92B2FsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldExpc3RTdHJ1Y3QkUGFyYW1zAAA=",
    ),  # single_value/single_value.capnp:SingleValue.getListStruct$Params
    (
        0xB50957424505E0A2,
        "ECpQBgb/ouAFRUJXCbUAESwBAAAFAQcAATEVEgIAAREtPwAB/3NpbmdsZV92B2FsdWUvc2luZ2xlX3ZhbHVlLmNhcG5wOlNpbmdsZVZhbHVlLmdldExpc3RTdHJ1Y3QkUmVzdWx0AXNRBAMEAAAEAQAAEQ0iAABRCAMBUSQCAQd2YWwBDgABUAMBARD/l1vQJZ6FY4oAAAEBDgAB",
    ),  # single_value/single_value.capnp:SingleValue.getListStruct$Results
    (
        0xBF602C4868DBB22F,
        "EBdQBgb/L7LbaEgsYL8AASgAAzEVcgERKRcAA/9mYnBfbmVzdARlZF9jYWxsYmFjay9mYnBfbmVzdGVkX2NhbGxiYWNrLh9jYXBucFEEAQH/6LHyLyvDYpwAEQFCf0NoYW5uZWw=",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp
    (
        0x9C62C32B2FF2B1E8,
        "ECdQBgb/6LHyLyvDYpwAES4D/y+y22hILGC/AAABMRaFAjEVsgERLRcAABE5RxFpBwAA/2ZicF9uZXN0BWVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2gfYW5uZWxRBAEB/wuSFRgKQzXcABEBcv9TdGF0c0NhbAAfbGJhY2tRBAMFAAD/MxN2ejseEJIBIyxx4NUIav4REbIAAhENB/9yZWdpc3RlcgFTdGF0c0NhbB9sYmFja0ABUAEB",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp:Channel
    (
        0xDC35430A1815920B,
        "ECpQBgb/C5IVGApDNdwAETYD/+ix8i8rw2KcAAABMSzxATEVIgIRNScAABFNRxF1BwAA/2ZicF9uZXN0B2VkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5TdGF0c0NhbGxiB2Fja1EIAQH/v114mpyuLqQAEQky/9nRfNd3ify5ABEFWh9TdGF0c/9VbnJlZ2lzdAADZXJRBAMFAAD/Y6GspZjy/IwBnYy7HMqoA64REToAAhEFBz9zdGF0dXNAAVABAQ==",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback
    (
        0xA42EAE9C9A785DBF,
        "EH1QBgb/v114mpyuLqQAUUQBA/8LkhUYCkM13AAFAQcAADGEhgExFVICETkHAAAxNVcBAAH/ZmJwX25lc3QIZWRfY2FsbGJhY2svZmJwX25lc3RlZF9jYWxsYmFjay5jYXBucDpDaGFubmVsLlN0YXRzQ2FsbGJhY2suU3RhdAFzUAEBURgDBAAABAEAABGZmgAAUZwDAVGoAgERAQEUAQEAABGlmgAAUagDAVG0AgERAgEUAQIAABGxegAAUbADAVG8AgERAwIUAQMAABG5qgAAUbwDAVHIAgEBBBQBBAAAEcVSAABRxAMBUdACAREFARQBBQAAEc2aAABR0AMBUdwCAf9ub09mV2FpdAFpbmdXcml0ZQNycwEHAAIBBwAB/25vT2ZXYWl0AWluZ1JlYWRlA3JzAQcAAgEHAAH/bm9PZklwc0kAP25RdWV1ZQEJAAIBCQAB/3RvdGFsTm9PAWZJcHNSZWNlD2l2ZWQBCQACAQkAAf90aW1lc3RhbQABcAEMAAIBDAAB/3VwZGF0ZUluAXRlcnZhbEluA01zAQgAAgEIAAE=",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.Stats
    (
        0xB9FC8977D77CD1D9,
        "ECRQBgb/2dF813eJ/LkAEUQD/wuSFRgKQzXcAAABM4wBzgExFXoCETkHAAARNUcRXQcAAP9mYnBfbmVzdAhlZF9jYWxsYmFjay9mYnBfbmVzdGVkX2NhbGxiYWNrLmNhcG5wOkNoYW5uZWwuU3RhdHNDYWxsYmFjay5VbnJlP2dpc3RlclABAVEEAwUAAP9tnAkonFz1iwGNL4MDvopA8RERMgACEQUHH3VucmVnQAFQAQE=",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.Unregister
    (
        0x8BF55C9C28099C6D,
        "EBlQBgb/bZwJKJxc9YsAEU8BAAAEBwABMRXiAgAE/2ZicF9uZXN0CmVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5TdGF0c0NhbGxiYWNrLlVucmVnaXN0ZXIudW5yZWckUGFyB2Ftcw==",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.Unregister.unreg$Params
    (
        0xF1408ABE03832F8D,
        "EClQBgb/jS+DA76KQPEAUU8BAQAABAcAATEV6gIAARE5PwAB/2ZicF9uZXN0CmVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5TdGF0c0NhbGxiYWNrLlVucmVnaXN0ZXIudW5yZWckUmVzD3VsdHNRBAMEAAAEAQAAEQ1CAABRCAMBURQCAX9zdWNjZXNzAQEAAgEBAAE=",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.Unregister.unreg$Results
    (
        0x8CFCF298A5ACA163,
        "EChQBgb/Y6GspZjy/IwAEUQBAAAFAQcAATEVkgIAARE1PwAB/2ZicF9uZXN0CWVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5TdGF0c0NhbGxiYWNrLnN0YXR1cyRQYXJhbQFzUQQDBAAABAEAABENMgAAUQgDAVEUAgEfc3RhdHMBEP+/XXianK4upAAAAQEQAAE=",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.status$Params
    (
        0xAE03A8CA1CBB8C9D,
        "EBhQBgb/nYy7HMqoA64AEUQBAAAEBwABMRWaAgAE/2ZicF9uZXN0CWVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5TdGF0c0NhbGxiYWNrLnN0YXR1cyRSZXN1bAN0cw==",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.StatsCallback.status$Results
    (
        0x92101E3B7A761333,
        "EDpQBgb/MxN2ejseEJIAUTYBAQAABQEHAAExFZoCAAERNXcAAf9mYnBfbmVzdAllZF9jYWxsYmFjay9mYnBfbmVzdGVkX2NhbGxiYWNrLmNhcG5wOkNoYW5uZWwucmVnaXN0ZXJTdGF0c0NhbGxiYWNrJFBhcmEDbXNRCAMEAAAEAQAAESlKAABRKAMBUTQCAQEBFAEBAAARMZoAAFE0AwFRQAIB/2NhbGxiYWNrAAAAARH/C5IVGApDNdwAAAEBEQAB/3VwZGF0ZUluAXRlcnZhbEluA01zAQgAAgEIAAE=",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.registerStatsCallback$Params
    (
        0xFE6A08D5E0712C23,
        "ECpQBgb/Iyxx4NUIav4AETYBAAAFAQcAATEVogIAARE1PwAB/2ZicF9uZXN0CWVkX2NhbGxiYWNrL2ZicF9uZXN0ZWRfY2FsbGJhY2suY2FwbnA6Q2hhbm5lbC5yZWdpc3RlclN0YXRzQ2FsbGJhY2skUmVzdQdsdHNRBAMEAAAEAQAAEQ2aAABREAMBURwCAf91bnJlZ2lzdAFlckNhbGxiYQNjawER/9nRfNd3ify5AAABAREAAQ==",
    ),  # fbp_nested_callback/fbp_nested_callback.capnp:Channel.registerStatsCallback$Results
]

_loader = capnp.SchemaLoader()
_loaded_bundle = False
_loaded_schema_ids: set[int] = set()


def _load_schema_node(schema_id: int, node_reader: _DynamicStructReader) -> _Schema:
    if schema_id in _loaded_schema_ids:
        return _loader.get(schema_id)
    loaded_schema = _loader.load_dynamic(node_reader)
    _loaded_schema_ids.add(schema_id)
    return loaded_schema


def _load_schema(schema: _Schema) -> _Schema:
    schema_id = int(schema.node.id)
    if schema_id in _loaded_schema_ids:
        return _loader.get(schema_id)
    loaded_schema = _loader.load(schema.get_proto())
    _loaded_schema_ids.add(schema_id)
    return loaded_schema


def _ensure_loaded() -> capnp.SchemaLoader:
    global _loaded_bundle
    if _loaded_bundle:
        return _loader

    for schema_id, schema_b64 in _SCHEMA_NODES:
        schema_data = base64.b64decode(schema_b64)
        node_reader = schema_capnp.Node.from_bytes_packed(schema_data)
        _load_schema_node(schema_id, node_reader)

    _loaded_bundle = True
    return _loader


def get_schema_loader() -> capnp.SchemaLoader:
    return _ensure_loaded()


def get_schema_by_id(schema_id: int) -> _Schema:
    return _ensure_loaded().get(schema_id)


def load_capnp_file(path: str, imports: list[str] | tuple[str, ...] = ()) -> object:
    parser = capnp.SchemaParser()
    module = parser.load(path, imports=list(imports))
    for parsed_module in parser.modules_by_id.values():
        schema = getattr(parsed_module, "schema", None)
        if schema is not None:
            _load_schema(schema)
    return module


__all__ = ["get_schema_by_id", "load_capnp_file"]
