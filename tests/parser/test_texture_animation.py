from pathlib import Path

import pytest

from mcanitexgen.parser import ParserError, Sequence, StateAction, TextureAnimation


class Test_FromJson:
    @pytest.mark.parametrize(
        "texture_path,expected_name,expected_texture",
        [
            ("head.png", "head", Path("head.png")),
            ("abc.jpg", "abc", Path("abc.jpg")),
        ],
    )
    def test_valid_texture_name(self, texture_path, expected_name, expected_texture):
        anim = TextureAnimation.from_json(texture_path, {"states": [], "main()": {}})
        assert anim.name == expected_name
        assert anim.texture == expected_texture

    @pytest.mark.parametrize("texture_path", ["abc.compressed.png", "   ", "a picture.png"])
    def test_invalid_texture_name(self, texture_path):
        with pytest.raises(ParserError, match="Invalid animation name.*"):
            TextureAnimation.from_json(texture_path, {"states": [], "main()": {}})

    def test_define_no_states(self):
        with pytest.raises(ParserError, match=".*does not define any states*"):
            TextureAnimation.from_json("abc.png", {"main()": {}})

    @pytest.mark.parametrize(
        "texture_path,json,expected",
        [
            (
                "head.png",
                {"states": ["A", "B", "C"], "main()": ["A", "B", "C"]},
                TextureAnimation(
                    "head",
                    Path("head.png"),
                    states=["A", "B", "C"],
                    sequences={
                        "main": Sequence(
                            "main",
                            actions=[StateAction("A"), StateAction("B"), StateAction("C")],
                        )
                    },
                ),
            )
        ],
    )
    def test(self, texture_path, json, expected):
        anim = TextureAnimation.from_json(texture_path, json)
        assert anim == expected
