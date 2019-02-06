# {
#   "intents": [
#     {
#       "label": "rate_swap",
#       "domain": "general",
#       "examples": [
#         "{currency} {coupon} {duration} {bid_ask} {quantity} {price}",
#         "{currency} {coupon} {duration} {bid_ask} {price} {quantity}",
#         "{currency} {coupon} {duration} {price} {bid_ask} {quantity}",
#         "{currency} {coupon} {duration} {quantity} {price} {bid_ask}"
#       ],
#       "composite_entities": [
#         {
#           "label": "price",
#           "spacing_threshold": 1,
#           "spacing": "",
#           "component_entity_patterns": [
#             ["quote_value"],
#             ["quote_value", "fraction"],
#             ["fraction"]
#           ]
#         },
#         {
#           "label": "quantity",
#           "spacing_threshold": 1,
#           "spacing": " ",
#           "component_entity_patterns": [
#             ["quote_value", "k"]
#           ]
#         }
#       ],
#       "structure_enforcement": "True"
#     },


