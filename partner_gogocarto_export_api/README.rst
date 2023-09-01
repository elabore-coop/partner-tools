============================
partner_gogocarto_export_api
============================

Gogocarto Export module, to export the partner data needed for a Gogocarto map.

This module allow the users to decide:

* the partners to be exported
* the fields exported for each partner (*name*, *partner_longitude* and *partner_lattitude* automatically exported)


Installation
============

Use Odoo normal module installation procedure to install
``partner_gogocarto_export_api``, all dependencies will be installed by default.

Configuration
=============

To export partners data:

#. Set the fields you want to export in Settings / Gogocarto.
#. Check the field *"Export to Gogocarto"* in the partner form view.

And use the link *https://yourodoo.com/web/<company_id>/get_http_gogocarto_elements* in Gogocarto server import configuration (*https://video.colibris-outilslibres.org/videos/watch/c74fc469-c822-4ab8-82a7-a2555e49e576*)


Known issues / Roadmap
======================

None yet.

Bug Tracker
===========

Bugs are tracked on `our issues website <https://github.com/elabore-coop/partner-tools/issues>`_. In case of
trouble, please check there if your issue has already been
reported. If you spotted it first, help us smashing it by providing a
detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Stéphan SAINLEGER <https://github.com/stephansainleger>
* Chloé Migayrou <https://github.com/MigayrouChloe>
* Nicolas Jeudy <https://github.com/njeudy>
* Lokavaluto Teams <https://lokavaluto.fr>

Funders
-------

The development of this module has been financially supported by:
* Lokavaluto (https://lokavaluto.fr)
* Mycéliandre (https://myceliandre.fr)
* Elabore (https://elabore.coop)


Maintainer
----------

This module is maintained by Elabore and Lokavaluto.