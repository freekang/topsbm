# This file is part of TopSBM
# Copyright 2017-8, Martin Gerlach and the University of Sydney
#
# TopSBM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TopSBM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TopSBM.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import pytest
from sklearn.utils.estimator_checks import check_estimator
from sklearn.datasets import fetch_20newsgroups, make_multilabel_classification
from sklearn.feature_extraction.text import CountVectorizer
from topsbm import TopSBM


X_mmlc, _ = make_multilabel_classification(n_samples=20, n_features=100)
bunch_20n = fetch_20newsgroups(categories=['alt.atheism',
                                           'soc.religion.christian'],
                               shuffle=True, random_state=0,
                               remove=('headers', 'footers'))
X_20n = CountVectorizer().fit_transform(bunch_20n.data)


def test_common():
    return check_estimator(TopSBM)


def test_trivial():
    X = np.zeros((20, 1000))
    X[:5, :200] = 1
    X[5:10, 200:210] = 1
    X[10:12, 210:500] = 1
    X[12:, 500:] = 1
    model = TopSBM(n_init=10)
    Xt = model.fit_transform(X)

    assert model.graph_ is not None
    assert model.state_ is not None
    assert model.mdl_ > 0
    assert model.num_features_ == 1000
    assert model.num_samples_ == 20

    print(Xt)
    print(model.groups_)
    assert Xt.shape == (20, 4)
    assert len(np.unique(Xt, axis=1)) == 4
    assert len(np.unique(Xt[:20], axis=1)) == 1
    assert len(np.unique(Xt[20:], axis=1)) == 1
    assert np.allclose(Xt.sum(axis=1), 1)
    assert np.allclose(np.ptp(Xt, axis=1), 1)


def test_n_init(n_samples=20, n_features=1000):
    feat = np.random.RandomState(0).choice(X_20n.shape[1], n_features)
    X = X_20n[:n_samples, feat]
    model1 = TopSBM(random_state=0).fit(X)
    model10 = TopSBM(random_state=0, n_init=10).fit(X)
    assert model10.mdl_ < model1.mdl_
    assert np.isclose(model1.state_.entropy(), model1.mdl_,
                      atol=0, rtol=1e-8)
    pytest.skip('Failure due to '
                'https://git.skewed.de/count0/graph-tool/issues/546')
    assert np.isclose(model10.state_.entropy(), model10.mdl_,
                      atol=0, rtol=1e-8)


def test_random_state(n_samples=20, n_features=100):
    feat = np.random.RandomState(0).choice(X_20n.shape[1], n_features)
    X = X_20n[:n_samples, feat]
    Xt0a = TopSBM(random_state=0).fit_transform(X)
    Xt0b = TopSBM(random_state=0).fit_transform(X)
    Xt2 = TopSBM(random_state=2).fit_transform(X)
    np.testing.assert_allclose(Xt0a, Xt0b)
    assert Xt0a.shape != Xt2.shape or not np.allclose(Xt0a, Xt2)
