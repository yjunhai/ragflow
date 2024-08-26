#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from abc import ABC
from agent.component.base import ComponentBase, ComponentParamBase


class SwitchParam(ComponentParamBase):
    """
    Define the Switch component parameters.
    """

    def __init__(self):
        super().__init__()
        """
        {
            "logical_operator" : "and | or"
            "items" : [
                            {"cpn_id": "categorize:0", "operator": "contains", "value": ""},
                            {"cpn_id": "categorize:0", "operator": "contains", "value": ""},...],
            "to": ""
        }
        """
        self.conditions = []
        self.end_cpn_id = "answer:0"
        self.operators = ['contains', 'not contains', 'start with', 'end with', 'empty', 'not empty', '=', '≠', '>',
                          '<', '≥', '≤']

    def check(self):
        self.check_empty(self.conditions, "[Switch] conditions")
        for cond in self.conditions:
            if not cond["to"]: raise ValueError(f"[Switch] 'To' can not be empty!")
            if cond["logical_operator"] not in ["and", "or"] and len(cond["items"]) > 1:
                raise ValueError(f"[Switch] Please set logical_operator correctly!")


class Switch(ComponentBase, ABC):
    component_name = "Switch"

    def _run(self, history, **kwargs):
        for cond in self._param.conditions:

            if len(cond["items"]) == 1:
                out = self._canvas.get_component(cond["items"][0]["cpn_id"])["obj"].output()[1]
                cpn_input = "" if "content" not in out.columns else " ".join(out["content"])
                if self.process_operator(cpn_input, cond["items"][0]["operator"], cond["items"][0]["value"]):
                    return Switch.be_output(cond["to"])
                continue

            if cond["logical_operator"] == "and":
                res = True
                for item in cond["items"]:
                    out = self._canvas.get_component(item["cpn_id"])["obj"].output()[1]
                    cpn_input = "" if "content" not in out.columns else " ".join(out["content"])
                    if not self.process_operator(cpn_input, item["operator"], item["value"]):
                        res = False
                        break
                if res:
                    return Switch.be_output(cond["to"])
                continue

            res = False
            for item in cond["items"]:
                out = self._canvas.get_component(item["cpn_id"])["obj"].output()[1]
                cpn_input = "" if "content" not in out.columns else " ".join(out["content"])
                if self.process_operator(cpn_input, item["operator"], item["value"]):
                    res = True
                    break
            if res:
                return Switch.be_output(cond["to"])

        return Switch.be_output(self._param.end_cpn_id)

    def process_operator(self, input: str, operator: str, value: str) -> bool:
        if not isinstance(input, str) or not isinstance(value, str):
            raise ValueError('Invalid input or value type: string')

        if operator == "contains":
            return True if value.lower() in input.lower() else False
        elif operator == "not contains":
            return True if value.lower() not in input.lower() else False
        elif operator == "start with":
            return True if input.lower().startswith(value.lower()) else False
        elif operator == "end with":
            return True if input.lower().endswith(value.lower()) else False
        elif operator == "empty":
            return True if not input else False
        elif operator == "not empty":
            return True if input else False
        elif operator == "=":
            return True if input == value else False
        elif operator == "≠":
            return True if input != value else False
        elif operator == ">":
            try:
                return True if float(input) > float(value) else False
            except Exception as e:
                return True if input > value else False
        elif operator == "<":
            try:
                return True if float(input) < float(value) else False
            except Exception as e:
                return True if input < value else False
        elif operator == "≥":
            try:
                return True if float(input) >= float(value) else False
            except Exception as e:
                return True if input >= value else False
        elif operator == "≤":
            try:
                return True if float(input) <= float(value) else False
            except Exception as e:
                return True if input <= value else False

        raise ValueError('Not supported operator' + operator)
